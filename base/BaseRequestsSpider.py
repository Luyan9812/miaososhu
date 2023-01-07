import time
import requests

import base.AgentInfo as Agent

from os.path import exists

from model.Book import Book
from base.Exceptions import self_catch
from service.DBService import DBService
from helper.EpubHelper import save_epub
from base.Exceptions import StatusException


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
        resp = requests.post(url, data=data, headers=self.headers())
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

    def scrape_full_book(self, book: Book, need_save=True):
        """ 爬取整本书 """
        turn = 0
        print(book.book_name)
        book_id = self.service.save_book(book)
        rows = self.service.query_catalogue_by_book_id(book_id=book_id)
        chapter_names = list(map(lambda x: x[3], filter(lambda x: not x[2] or x[2] < 0, rows)))
        for i, ch in enumerate(book.catalogue.items(), start=1):
            ch_name, ch_url = ch
            if ch_name not in chapter_names: continue
            turn += 1
            chapter = self.scrape_chapter(ch_url)
            chapter.order_id = i
            chapter.display_name = ch_name
            book.current_chapter += 1
            chapter_id = self.service.save_chapter(book_id=book_id, chapter=chapter)
            chapter.chapter_id = chapter_id
            if turn % self.fetch_interval == 0:
                time.sleep(self.sleep_time)
        chapters = self.service.query_chapter_by_bookid(book_id=book_id)
        book.chapter_list.extend(chapters)
        book.current_chapter = len(chapters)
        if need_save: self.save(book=book)
        return book

    @self_catch
    def hot_list(self):
        """ 返回热榜书籍列表 """
        html = self.fetch(self.hot_url)
        books = self._parse_hot_list(html)
        return books

    @self_catch
    def search(self, keyword: str, page=1):
        """ 根据关键字和页码获取书籍列表 """
        params = {"keyword": keyword, 'page': page}
        html = self.fetch(self.search_url, params=params)
        current_page, total_page, books = self._parse_search_page(html)
        return current_page, total_page, books

    @self_catch
    def scrape_book_index(self, url):
        """ 爬取某本书的首页 """
        html = self.fetch(url)
        book = self._parse_book_index(html)
        book.url = url
        return book

    @self_catch
    def scrape_chapter(self, chapter_url):
        """ 根据链接爬取某一个章节内容 """
        html = self.fetch(chapter_url)
        chapter = self._parse_chapter(html)
        chapter.url = chapter_url
        # 爬取的时候输出当前爬哪一章
        print('\t' + chapter.display_name)
        return chapter

    def save(self, book: Book):
        """ 保存书籍 """
        content = None
        try:
            content = None if exists(book.save_img_path) else self.fetch_b(book.cover_img)
        except StatusException as e:
            print(e)
        finally:
            book.save(content)
            save_epub(book)

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
