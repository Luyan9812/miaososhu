import os
import time
import requests

import base.AgentInfo as Agent

from os.path import exists
from model.Book import Book
from base.Exceptions import self_catch
from service.DBService import DBService
from helper.EpubHelper import save_epub
from base.Exceptions import StatusException


def save_txt(book: Book):
    """ 将小说保存成 txt 格式 """
    with open(book.save_txt_path, 'w') as f:
        f.write("书籍描述信息\n\n" + book.desc())
        for chapter in book.chapter_list:
            f.write('\n\n\n' + chapter.display_name + '\n\n')
            f.write(chapter.content)


class BaseRequestsSpider(object):

    def __init__(self):
        self.encoding = 'utf-8'
        self.tag = ''
        self.img_tag = ''
        self.hot_url = ''
        self.base_url = ''
        self.search_url = ''

        self.sleep_time = 5  # 每次休眠时间（s）
        self.fetch_interval = 150  # 每爬取多少次休眠一次

        self.service = DBService()

    def headers(self):
        """ 网站请求头的封装 """
        cookie = Agent.cookies[self.tag]
        return {'User-Agent': Agent.USER_AGENT, 'Cookie': cookie}

    def headers_b(self):
        """ 请求二进制文件时的请求头 """
        return self.headers()

    def fetch(self, url: str, params=None):
        """ 根据给定的 url 获取网页代码 """
        resp = requests.get(url, params=params, headers=self.headers())
        if resp.status_code != 200:
            raise StatusException(url, resp.status_code)
        resp.encoding = self.encoding
        return resp.text

    def fetch_post(self, url, data=None):
        """ 使用 post 方式获取网页代码 """
        try:
            resp = requests.post(url, data=data, headers=self.headers())
        except requests.exceptions.RequestException as e:
            raise StatusException(url, e.errno)
        if resp.status_code != 200:
            raise StatusException(url, resp.status_code)
        resp.encoding = self.encoding
        return resp.text

    def fetch_b(self, url: str):
        """ 根据给定的 url 获取二进制数据流 """
        resp = requests.get(url, headers=self.headers_b())
        if resp.status_code != 200:
            raise StatusException(url, resp.status_code)
        return resp.content

    def get_search_dict(self, keyword, page=1):
        """ 获取搜索键值对 """
        return {}

    @self_catch
    def search(self, keyword: str, page=1):
        """ 搜索书籍 """
        return self.search_post(keyword=keyword, page=page)

    def search_get(self, keyword: str, page=1):
        """ 根据关键字和页码获取书籍列表 """
        params = self.get_search_dict(keyword=keyword, page=page)
        html = self.fetch(url=self.search_url, params=params)
        current_page, total_page, books = self._parse_search_page(html)
        return current_page, total_page, books

    def search_post(self, keyword: str, page=1):
        """ 根据关键字和页码获取书籍列表 """
        params = self.get_search_dict(keyword=keyword, page=page)
        html = self.fetch_post(url=self.search_url, data=params)
        current_page, total_page, books = self._parse_search_page(html)
        return current_page, total_page, books

    def scrape_full_book(self, book: Book, need_save=True, force_generate_file=False):
        """ 爬取整本书 """
        turn = 0
        print(f'\n《{book.book_name}》')
        if not self.service.should_scrape(book):
            print('书籍来源不匹配，不予爬取')
            return None
        book_id, _ = self.service.save_book(book, need_update=True)
        rows = self.service.query_catalogue_by_bookid_without_cid(book_id=book_id)
        chapter_names = list(map(lambda x: x[0], rows))
        for i, ch in enumerate(book.catalogue, start=1):
            ch_name, ch_url = ch.chapter_name, ch.chapter_url
            if ch_name not in chapter_names: continue
            turn += 1
            print(f'《{book.book_name}》\t{i}/{book.total_chapter}', end='')
            chapter = self.scrape_chapter(ch_url)
            chapter.order_id = i
            chapter.display_name = ch_name
            book.current_chapter += 1
            chapter_id = self.service.save_chapter(book_id=book_id, chapter=chapter)
            chapter.chapter_id = chapter_id
            if turn % self.fetch_interval == 0:
                time.sleep(self.sleep_time)
        if turn == 0:
            print("没有更新")
            if not force_generate_file: return book
        chapters = self.service.query_chapter_by_bookid(book_id=book_id)
        book.chapter_list = chapters
        book.current_chapter = len(chapters)
        if need_save or force_generate_file: self.save(book=book)
        return book

    @self_catch
    def hot_list(self):
        """ 返回热榜书籍列表 """
        html = self.fetch(self.hot_url)
        books = self._parse_hot_list(html)
        return books

    @self_catch
    def scrape_book_index(self, url: str):
        """ 爬取某本书的首页 """
        html = self.fetch(url)
        book = self._parse_book_index(html)
        book.url = url
        return book

    @self_catch
    def scrape_chapter(self, chapter_url: str):
        """ 根据链接爬取某一个章节内容 """
        html = self.fetch(chapter_url)
        chapter = self._parse_chapter(html)
        chapter.url = chapter_url
        # 爬取的时候输出当前爬哪一章
        print('\t' + chapter.display_name)
        return chapter

    def save_cover_img(self, book: Book):
        """ 保存封面图 """
        try:
            content = None if exists(book.save_img_path) else self.fetch_b(book.cover_img)
            if content is None: return
            with open(book.save_img_path, 'wb') as f:
                f.write(content)
        except StatusException as e:
            print(e)

    def save(self, book: Book, need_txt=False):
        """ 保存书籍 """
        self.save_cover_img(book=book)
        save_epub(book)
        if need_txt:
            save_txt(book=book)
        print(f'书籍《{book.book_name}》保存成功')

    def _parse_hot_list(self, html):
        """
        解析热榜界面
        :param html: 网页源代码
        :return: 书籍列表
        """
        raise NotImplementedError

    def _parse_search_page(self, html):
        """
        解析搜索界面
        :param html: 网页源代码
        :return: (当前页码，总页码，书籍列表)
        """
        raise NotImplementedError

    def _parse_book_index(self, html):
        """
        解析书籍目录页
        :param html: 网页源代码
        :return: 书籍信息，包括了章节名称及章节链接
        """
        raise NotImplementedError

    def _parse_chapter(self, html):
        """
        解析章节页面
        :param html: 网页源代码
        :return: 章节内容
        """
        raise NotImplementedError


def main():
    """ 测试函数 """
    project_name = 'miaososhu/'
    absp = os.path.abspath(os.path.dirname(__file__))
    posi = absp.rfind(project_name) + len(project_name)
    print(absp[:posi])


if __name__ == '__main__':
    main()
