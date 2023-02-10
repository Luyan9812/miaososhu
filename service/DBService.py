import os
import time
import logging
import helper.ListHelper as ListHelper

from model.User import User
from model.Book import Book
from model.Chapter import Chapter
from model.Catalogue import Catalogue
from model.DownloadItem import DownloadItem
from helper.DBHelper import MysqlHelper


class DBService(object):
    """ 操作数据库的封装类 """

    def __init__(self):
        self.db_helper = MysqlHelper(dbname='miao_novel')
        self.__on_check()
        self.TABLE_BOOK = 'book'
        self.TABLE_USER = 'users'
        self.TABLE_CHAPTER = 'chapter'
        self.TABLE_CATALOGUE = 'catalogue'
        self.TABLE_DOWNLOAD_QUEUE = 'download_queue'
        self.TABLE_AUTHORITY_CODES = 'authority_codes'
        self.TABLE_DAILY_RECOMMENDATION = 'daily_recommendation'

    def __del__(self):
        self.db_helper.onclose()

    def __on_check(self):
        """ 检查表是否存在 """
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, '../helper/建表语句.txt')
        with open(path, 'r') as f:
            for sql in ListHelper.remove_empty(f.read().split(';')):
                self.db_helper.execute(sql + ';')

    def _query_one_by_cond_yield(self, table_name, condition, order_by=None, converter=None):
        """ 按照条件每次查询一条记录返回 """
        cnt = self._count_by_cond(table_name=table_name, condition=condition)
        if converter is None:
            converter = lambda x: x
        for i in range(cnt):
            row = self.db_helper.query_one(table_name=table_name, condition=condition,
                                           order_by=order_by, limit=f' {i}, 1 ')
            yield converter(row)

    def _count_by_cond(self, table_name, condition):
        """ 根据条件获取记录条数 """
        return self.db_helper.count(table_name=table_name, condition=condition)

    def query_type(self, type_name):
        """ 查询类别信息 """
        condition = f'type_name="{type_name}" '
        return self.db_helper.query_one(table_name='book_type', condition=condition)

    def query_type_by_id(self, type_id):
        """ 根据 id 查询类别信息 """
        condition = f'id={type_id} '
        return self.db_helper.query_one(table_name='book_type', condition=condition)

    def save_type(self, type_name):
        """ 存储类别信息 """
        data = {'type_name': type_name}
        t = self.query_type(type_name=type_name)
        if t: return t[0]
        type_id = self.db_helper.insert(table_name='book_type', data=data)
        return type_id

    def __generate_book(self, row: tuple, need_catalogue=False):
        """ 查询出来的元组生成 Book 对象 """
        if not row: return None
        book_id, book_name, author_name, book_type_id, finish_status, update_time, url, cover_img, info = row
        book_type = self.query_type_by_id(book_type_id)
        book = Book(book_name=book_name, author_name=author_name, update_time=update_time, book_type=book_type[1],
                    info=info, finish_status=finish_status, url=url, cover_img=cover_img, book_id=book_id)
        catalogue = []
        if need_catalogue:
            for row in self.query_catalogue_by_book_id(book_id=book_id):
                catalogue_id, book_id, chapter_id, chapter_name, chapter_url = row
                catalogue.append(Catalogue(chapter_name=chapter_name, chapter_url=chapter_url,
                                           catalogue_id=catalogue_id, book_id=book_id, chapter_id=chapter_id))
            book.total_chapter = len(catalogue)
            book.current_chapter = self.count_chapter(book_id=book_id)
        book.catalogue = catalogue
        return book

    def query_book_by_bookname_authorname(self, book_name, author_name):
        """ 按照书名、作者名精确查找书籍 """
        condition = f'book_name="{book_name}" AND author_name="{author_name}" '
        row = self.db_helper.query_one(table_name=self.TABLE_BOOK, condition=condition)
        book = self.__generate_book(row)
        return book

    def query_book_by_id(self, book_id, need_catalogue=False):
        """ 根据 id 查找书籍 """
        condition = f'id={book_id} '
        row = self.db_helper.query_one(table_name=self.TABLE_BOOK, condition=condition)
        book = self.__generate_book(row, need_catalogue=need_catalogue)
        return book

    def query_book_like(self, kw, con=''):
        """ 根据书名模糊匹配 """
        books = []
        condition = f'book_name LIKE "%{kw}%" '
        if con: condition += con
        for row in self.db_helper.query_list(table_name=self.TABLE_BOOK, condition=condition):
            book = self.__generate_book(row=row)
            books.append(book)
        return books

    def query_book_by_author_like(self, author_name, con=''):
        """ 根据作者名模糊查找书籍 """
        books = []
        condition = f'author_name LIKE "%{author_name}%" '
        if con: condition += con
        for row in self.db_helper.query_list(table_name=self.TABLE_BOOK, condition=condition):
            book = self.__generate_book(row)
            books.append(book)
        return books

    def query_book_by_book_author_like(self, book_name, author_name, con=''):
        """ 根据书名、作者名模糊查找书籍 """
        books = []
        condition = f'book_name LIKE "%{book_name}%" AND author_name LIKE "%{author_name}%" '
        if con: condition += con
        for row in self.db_helper.query_list(table_name=self.TABLE_BOOK, condition=condition):
            book = self.__generate_book(row)
            books.append(book)
        return books

    def query_all_books(self):
        """ 查询所有书籍 """
        yield from self._query_one_by_cond_yield(table_name=self.TABLE_BOOK,
                                                 condition='1=1 ', converter=self.__generate_book)

    def query_all_books_list(self):
        """ 查询所有书籍，以列表返回 """
        rows = self.db_helper.query_list(table_name=self.TABLE_BOOK, condition=' 1=1 ')
        if not rows: return None
        books = []
        for row in rows:
            book = self.__generate_book(row=row)
            books.append(book)
        return books

    def query_all_books_id(self, con=''):
        """ 查询所有本站书籍的id """
        condition = '1=1 '
        if con: condition += con
        return self.db_helper.query_list(table_name=self.TABLE_BOOK, condition=condition, fields=['id'])

    def query_book_by_finish_status(self, is_finish):
        """ 根据完结状态查询书籍 """
        condition = f'finish_status={is_finish} '
        yield from self._query_one_by_cond_yield(table_name=self.TABLE_BOOK,
                                                 condition=condition, converter=self.__generate_book)

    def count_books_by_condition(self, condition):
        """ 按照条件获取书籍的数目 """
        nums = self.db_helper.count(table_name=self.TABLE_BOOK, condition=condition)
        return nums

    def query_book_by_condition(self, condition, limit=None):
        """ 根据条件查询书籍 """
        books = []
        rows = self.db_helper.query_list(table_name=self.TABLE_BOOK, condition=condition, limit=limit)
        if not rows: return books
        for row in rows:
            books.append(self.__generate_book(row=row))
        return books

    def query_book_by_website(self, baseurl):
        """ 根据所属网站查询书籍 """
        condition = f'url LIKE "{baseurl}%" '
        yield from self._query_one_by_cond_yield(table_name=self.TABLE_BOOK,
                                                 condition=condition, converter=self.__generate_book)

    def update_book_by_id(self, book_id, data: dict):
        """ 通过书籍 id 更新书籍信息 """
        condition = f'id={book_id} '
        self.db_helper.update(table_name=self.TABLE_BOOK, data=data, condition=condition)

    def should_scrape(self, book: Book):
        """
        判断是否应该爬取 book
        按照书名与作者名查询，满足以下任一条件的才允许爬取：
        1. 数据库中不存在该书籍
        2. 数据库存在且要爬取的站点与数据库中的一致（保证数据的一致性）
        """
        b = self.query_book_by_bookname_authorname(book_name=book.book_name, author_name=book.author_name)
        return b is None or b.url == book.url

    def save_book(self, book: Book, need_update=False):
        """ 存储书籍 """
        type_id = self.save_type(book.book_type)
        b = self.query_book_by_bookname_authorname(book_name=book.book_name, author_name=book.author_name)
        if not b:
            data = book.get_db_dict()
            data['book_type_id'] = type_id
            book_id = self.db_helper.insert(table_name=self.TABLE_BOOK, data=data)
            book.book_id = book_id
        else:
            if need_update:
                data = {'finish_status': book.finish_status, 'update_time': f"'{book.update_time}'",
                        'info': f"'{book.info}'", 'book_type_id': type_id}
                self.update_book_by_id(book_id=b.book_id, data=data)
            book.book_id = book_id = b.book_id
        self.save_catalogues(book)
        return book_id, not b

    def count_catalogue(self, book_id):
        """ 根据书籍 id 统计目录条数 """
        condition = f'book_id={book_id} '
        return self.db_helper.count(table_name=self.TABLE_CATALOGUE, condition=condition)

    def query_catalogue_one(self, book_id, chapter_name):
        """ 根据书籍 id 和章节名称唯一确定目录 """
        condition = f'book_id={book_id} AND chapter_name="{chapter_name}" '
        return self.db_helper.query_one(table_name=self.TABLE_CATALOGUE, condition=condition)

    def query_catalogue_by_book_id(self, book_id, order_by=None, limit=None):
        """ 根据书籍 id 查询目录 """
        condition = f'book_id={book_id} '
        return self.db_helper.query_list(table_name=self.TABLE_CATALOGUE,
                                         condition=condition, order_by=order_by, limit=limit)

    def query_catalogue_by_bookid_without_cid(self, book_id, order_by=None, limit=None):
        condition = f'book_id={book_id} AND (chapter_id IS NULL OR chapter_id<0) '
        return self.db_helper.query_list(table_name=self.TABLE_CATALOGUE,
                                         condition=condition, order_by=order_by, limit=limit, fields=['chapter_name'])

    def query_catalogue_by_chapter_id(self, chapter_id):
        """ 根据章节 id 查询目录 """
        condition = f'chapter_id={chapter_id} '
        return self.db_helper.query_one(table_name=self.TABLE_CATALOGUE, condition=condition)

    def update_catalogue_by_bid_cname(self, book_id, chapter_name, data):
        """ 根据书籍 id 和章节名称更新目录 """
        condition = f'book_id={book_id} and chapter_name="{chapter_name}" '
        self.db_helper.update(table_name=self.TABLE_CATALOGUE, data=data, condition=condition)

    def save_catalogue_one(self, book_id, chapter_name, chapter_url):
        """ 存储一条的目录 """
        c = self.query_catalogue_one(book_id=book_id, chapter_name=chapter_name)
        if c: return c[0]
        data = {'book_id': book_id, 'chapter_name': chapter_name, 'chapter_url': chapter_url}
        return self.db_helper.insert(table_name=self.TABLE_CATALOGUE, data=data)

    def save_catalogues(self, book: Book):
        """ 存储一本书的目录 """
        for item in book.catalogue:
            self.save_catalogue_one(book_id=book.book_id, chapter_name=item.chapter_name, chapter_url=item.chapter_url)

    def __generate_chapter(self, row):
        """ 查询出来的元组生成 Chapter 对象 """
        if not row: return None
        chapter_id, book_id, order_id, display_name, content = row
        chapter = Chapter(display_name=display_name, content=content, url='',
                          chapter_id=chapter_id, order_id=order_id, book_id=book_id)
        catalogue = self.query_catalogue_by_chapter_id(chapter_id)
        if catalogue:
            chapter.url = catalogue[4]
        else:
            logging.error('Here is error!')
        return chapter

    def count_chapter(self, book_id):
        """ 根据书籍 id 统计章节数目 """
        condition = f'book_id={book_id} '
        return self._count_by_cond(table_name=self.TABLE_CHAPTER, condition=condition)

    def query_chapter_by_bookid(self, book_id, limit=None):
        """ 根据书籍 id 获取章节 """
        chapters = []
        condition = f'book_id={book_id} '
        for row in self.db_helper.query_list(table_name=self.TABLE_CHAPTER,
                                             condition=condition, order_by='order_id', limit=limit):
            chapter = self.__generate_chapter(row)
            chapters.append(chapter)
        return chapters

    def query_chapter_by_bookid_yield(self, book_id):
        """ 根据书籍 id 获取章节（章节一个个返回） """
        condition = f'book_id={book_id} '
        yield from self._query_one_by_cond_yield(table_name=self.TABLE_CHAPTER, condition=condition,
                                                 order_by='order_id', converter=self.__generate_chapter)

    def query_chapter_one(self, book_id, display_name):
        """ 根据书籍 id 和 章节名称唯一确定一个章节 """
        condition = f'book_id={book_id} AND display_name="{display_name}" '
        row = self.db_helper.query_one(table_name=self.TABLE_CHAPTER, condition=condition)
        return self.__generate_chapter(row)

    def query_chapter_by_id(self, chapter_id):
        """ 根据 id 查找章节 """
        condition = f'id={chapter_id} '
        row = self.db_helper.query_one(table_name=self.TABLE_CHAPTER, condition=condition)
        return self.__generate_chapter(row)

    def update_chapter_by_cid(self, cid, data: dict):
        """ 根据章节 id 更新章节信息 """
        condition = f'id={cid} '
        self.db_helper.update(table_name=self.TABLE_CHAPTER, data=data, condition=condition)

    def update_chapter_by_bid_cname(self, book_id, display_name, data):
        """ 根据书籍 id 和章节名称更新目录 """
        condition = f'book_id={book_id} and display_name="{display_name}" '
        self.db_helper.update(table_name=self.TABLE_CHAPTER, data=data, condition=condition)

    def save_chapter(self, book_id, chapter: Chapter):
        """ 保存章节信息 """
        ch = self.query_chapter_one(book_id=book_id, display_name=chapter.display_name)
        if not ch:
            data = {'book_id': book_id, 'order_id': chapter.order_id,
                    'display_name': chapter.display_name, 'content': chapter.content}
            chapter_id = self.db_helper.insert(table_name=self.TABLE_CHAPTER, data=data)
        else:
            chapter_id = ch.chapter_id
        data = {'chapter_id': chapter_id}
        self.update_catalogue_by_bid_cname(book_id=book_id, chapter_name=chapter.display_name, data=data)
        return chapter_id

    def query_commend_by_id(self, comm_id):
        """ 根据 id 查询每日推荐 """
        condition = f'id={comm_id} '
        row = self.db_helper.query_one(table_name=self.TABLE_DAILY_RECOMMENDATION, condition=condition)
        return {'id': row[0], 'book_id': row[1], 'recommend_date': row[2], 'resource': row[3]}

    def query_commend_by_date(self, recommend_date, resource):
        """
        根据日期和来源查询每日推荐
        :param recommend_date: 日期
        :param resource: 来源。0-本站资源，1-外站资源
        :return 当前日期、来源的推荐书籍的 id 列表
        """
        condition = f'recommend_date={recommend_date} AND resource={resource} '
        rows = self.db_helper.query_list(table_name=self.TABLE_DAILY_RECOMMENDATION,
                                         condition=condition, fields=['book_id'])
        return list(map(lambda x: x[0], rows)) if rows else []

    def save_commend(self, book_id, recommend_date, resource):
        """ 保存一条每日推荐 """
        data = {'book_id': book_id, 'recommend_date': recommend_date, 'resource': resource}
        com_id = self.db_helper.insert(table_name=self.TABLE_DAILY_RECOMMENDATION, data=data)
        return com_id

    def query_download_item_by_id(self, qid):
        """ 根据 id 查询一条下载记录 """
        condition = f' id={qid} '
        row = self.db_helper.query_one(table_name=self.TABLE_DOWNLOAD_QUEUE, condition=condition)
        if not row: return None
        qid, url, download_state = row
        return DownloadItem(url=url, download_state=download_state, qid=qid)

    def query_download_item_by_url(self, url):
        """ 根据 url 查询下载记录 """
        condition = f" url='{url}' "
        row = self.db_helper.query_one(table_name=self.TABLE_DOWNLOAD_QUEUE, condition=condition)
        if not row: return None
        qid, url, download_state = row
        return DownloadItem(url=url, download_state=download_state, qid=qid)

    def query_download_item_by_state(self, download_state):
        """ 根据状态查询一条下载记录 """
        condition = f' download_state={download_state} '
        row = self.db_helper.query_one(table_name=self.TABLE_DOWNLOAD_QUEUE, condition=condition, limit='1')
        if not row: return None
        qid, url, download_state = row
        return DownloadItem(url=url, download_state=download_state, qid=qid)

    def update_download_item_by_id(self, download_item):
        """ 根据 id 更新下载记录 """
        condition = f' id={download_item.qid} '
        data = {'url': f"'{download_item.url}'", 'download_state': download_item.download_state}
        self.db_helper.update(table_name=self.TABLE_DOWNLOAD_QUEUE, data=data, condition=condition)

    def save_download_item(self, url, download_state):
        """
        保存一条下载记录
        :param url: 待下载的 url
        :param download_state: 下载状态。0：待下载；1：下载中；2：下载成功；-1：下载失败。
        :return:
        """
        data = {'url': url, 'download_state': download_state}
        qid = self.db_helper.insert(table_name=self.TABLE_DOWNLOAD_QUEUE, data=data)
        return qid

    def query_authcode_by_id(self, aid):
        """ 根据 id 查询鉴权码 """
        condition = f' id={aid} '
        row = self.db_helper.query_one(table_name=self.TABLE_AUTHORITY_CODES, condition=condition)
        return row

    def query_authcode_by_code(self, code):
        """ 根据码来查询 """
        condition = f' auth_code="{code}" '
        row = self.db_helper.query_one(table_name=self.TABLE_AUTHORITY_CODES, condition=condition)
        return row

    def query_all_authcode(self):
        """ 查询所有鉴权码 """
        condition = ' 1=1 '
        rows = self.db_helper.query_list(table_name=self.TABLE_AUTHORITY_CODES, condition=condition)
        if not rows: return None
        return rows

    def update_authcode(self, aid, valid_times):
        """ 修改鉴权码的有效次数 """
        condition = f' id={aid} '
        data = {'valid_times': valid_times}
        self.db_helper.update(table_name=self.TABLE_AUTHORITY_CODES, data=data, condition=condition)

    def delete_authcode(self, aid):
        """ 删除鉴权码 """
        condition = f' id={aid} '
        self.db_helper.delete(table_name=self.TABLE_AUTHORITY_CODES, condition=condition)

    def save_authcode(self, code, valid_times):
        """ 新增一条鉴权码 """
        data = {'auth_code': code, 'valid_times': valid_times}
        aid = self.db_helper.insert(table_name=self.TABLE_AUTHORITY_CODES, data=data)
        return aid

    def query_user_by_id(self, uid):
        """ 根据 id 查询用户 """
        condition = f' uid={uid} '
        row = self.db_helper.query_one(table_name=self.TABLE_USER, condition=condition)
        if not row: return None
        uid, uname, upassword, urole, umail = row
        return User(uname=uname, upassword=upassword, urole=urole, umail=umail, uid=uid)

    def query_user_by_name_password(self, uname, upassword):
        """ 根据用户名、密码查询用户 """
        condition = f' uname="{uname}" and upassword="{upassword}" '
        row = self.db_helper.query_one(table_name=self.TABLE_USER, condition=condition)
        if not row: return None
        uid, uname, upassword, urole, umail = row
        return User(uname=uname, upassword=upassword, urole=urole, umail=umail, uid=uid)


def main():
    service = DBService()
    chapters = service.query_commend_by_date(recommend_date='2023-2-5', resource=0)
    print(chapters)


if __name__ == '__main__':
    main()
