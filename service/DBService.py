import logging
import os
import helper.ListHelper as ListHelper

from model.Book import Book
from model.Chapter import Chapter
from helper.DBHelper import MysqlHelper


class DBService(object):
    """ 操作数据库的封装类 """

    def __init__(self):
        self.db_helper = MysqlHelper(dbname='miao_novel')
        self.__on_check()

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

    def __generate_book(self, row: tuple):
        """ 查询出来的元组生成 Book 对象 """
        if not row: return None
        book_id, book_name, author_name, book_type_id, finish_status, update_time, url, cover_img, info = row
        book_type = self.query_type_by_id(book_type_id)
        book = Book(book_name=book_name, author_name=author_name, update_time=update_time, book_type=book_type[1],
                    info=info, finish_status=finish_status, url=url, cover_img=cover_img, book_id=book_id)
        catalogue = {}
        for row in self.query_catalogue_by_book_id(book_id=book_id):
            _, _, _, chapter_name, chapter_url = row
            catalogue[chapter_name] = chapter_url
        book.catalogue = catalogue
        book.total_chapter = len(catalogue)
        book.current_chapter = self.count_chapter(book_id=book_id)
        return book

    def query_book_one(self, book: Book):
        """ 按照书名、作者名精确查找书籍 """
        condition = f'book_name="{book.book_name}" AND author_name="{book.author_name}" '
        row = self.db_helper.query_one(table_name='book', condition=condition)
        book = self.__generate_book(row)
        return book

    def query_book_like(self, kw):
        """ 根据书名模糊匹配 """
        books = []
        condition = f'book_name LIKE "%{kw}%" '
        for row in self.db_helper.query_list(table_name='book', condition=condition):
            book = self.__generate_book(row=row)
            books.append(book)
        return books

    def query_book_by_id(self, book_id):
        """ 根据 id 查找书籍 """
        condition = f'id={book_id} '
        row = self.db_helper.query_one(table_name='book', condition=condition)
        book = self.__generate_book(row)
        return book

    def query_book_by_author(self, author_name):
        """ 根据作者名查找书籍 """
        books = []
        condition = f'author_name="{author_name}" '
        for row in self.db_helper.query_list(table_name='book', condition=condition):
            book = self.__generate_book(row)
            books.append(book)
        return books

    def query_all_books(self):
        """ 查询所有书籍 """
        yield from self._query_one_by_cond_yield(table_name='book', condition='1=1 ', converter=self.__generate_book)

    def query_book_by_finish_status(self, is_finish):
        """ 根据完结状态查询书籍 """
        condition = f'finish_status={is_finish} '
        yield from self._query_one_by_cond_yield(table_name='book', condition=condition, converter=self.__generate_book)

    def query_book_by_website(self, baseurl):
        """ 根据所属网站查询书籍 """
        condition = f'url LIKE "{baseurl}%" '
        yield from self._query_one_by_cond_yield(table_name='book', condition=condition, converter=self.__generate_book)

    def save_book(self, book: Book):
        """ 存储书籍 """
        b = self.query_book_one(book)
        if not b:
            data = book.get_db_dict()
            type_id = self.save_type(book.book_type)
            data['book_type_id'] = type_id
            book_id = self.db_helper.insert(table_name='book', data=data)
            book.book_id = book_id
        else: book.book_id = book_id = b.book_id
        self.save_catalogues(book)
        return book_id

    def count_catalogue(self, book_id):
        """ 根据书籍 id 统计目录条数 """
        condition = f'book_id={book_id} '
        return self.db_helper.count(table_name='catalogue', condition=condition)

    def query_catalogue_one(self, book_id, chapter_name):
        """ 根据书籍 id 和章节名称唯一确定目录 """
        condition = f'book_id={book_id} AND chapter_name="{chapter_name}" '
        return self.db_helper.query_one(table_name='catalogue', condition=condition)

    def query_catalogue_by_book_id(self, book_id):
        """ 根据书籍 id 查询目录 """
        condition = f'book_id={book_id} '
        return self.db_helper.query_list(table_name='catalogue', condition=condition)

    def query_catalogue_by_chapter_id(self, chapter_id):
        """ 根据章节 id 查询目录 """
        condition = f'chapter_id={chapter_id} '
        return self.db_helper.query_one(table_name='catalogue', condition=condition)

    def update_catalogue_by_bid_cname(self, book_id, chapter_name, data):
        """ 根据书籍 id 和章节名称更新目录 """
        condition = f'book_id={book_id} and chapter_name="{chapter_name}" '
        self.db_helper.update(table_name='catalogue', data=data, condition=condition)

    def save_catalogue_one(self, book_id, chapter_name, chapter_url):
        """ 存储一条的目录 """
        c = self.query_catalogue_one(book_id=book_id, chapter_name=chapter_name)
        if c: return c[0]
        data = {'book_id': book_id, 'chapter_name': chapter_name, 'chapter_url': chapter_url}
        return self.db_helper.insert(table_name='catalogue', data=data)

    def save_catalogues(self, book: Book):
        """ 存储一本书的目录 """
        for k, v in book.catalogue.items():
            self.save_catalogue_one(book_id=book.book_id, chapter_name=k, chapter_url=v)

    def __generate_chapter(self, row):
        """ 查询出来的元组生成 Chapter 对象 """
        if not row: return None
        chapter_id, book_id, order_id, display_name, content = row
        chapter = Chapter(display_name=display_name, content=content, url='', chapter_id=chapter_id, order_id=order_id)
        catalogue = self.query_catalogue_by_chapter_id(chapter_id)
        if catalogue: chapter.url = catalogue[4]
        else:
            logging.error('Here is error!')
        return chapter

    def count_chapter(self, book_id):
        """ 根据书籍 id 统计章节数目 """
        condition = f'book_id={book_id} '
        return self._count_by_cond(table_name='chapter', condition=condition)

    def query_chapter_by_bookid(self, book_id, limit=None):
        """ 根据书籍 id 获取章节 """
        chapters = []
        condition = f'book_id={book_id} '
        for row in self.db_helper.query_list(table_name='chapter', condition=condition, order_by='order_id', limit=limit):
            chapter = self.__generate_chapter(row)
            chapters.append(chapter)
        return chapters

    def query_chapter_by_bookid_yield(self, book_id):
        """ 根据书籍 id 获取章节（章节一个个返回） """
        condition = f'book_id={book_id} '
        yield from self._query_one_by_cond_yield(table_name='chapter', condition=condition,
                                                 order_by='order_id', converter=self.__generate_chapter)

    def query_chapter_one(self, book_id, display_name):
        """ 根据书籍 id 和 章节名称唯一确定一个章节 """
        condition = f'book_id={book_id} AND display_name="{display_name}" '
        row = self.db_helper.query_one(table_name='chapter', condition=condition)
        return self.__generate_chapter(row)

    def query_chapter_by_id(self, chapter_id):
        """ 根据 id 查找章节 """
        condition = f'id={chapter_id} '
        row = self.db_helper.query_one(table_name='chapter', condition=condition)
        return self.__generate_chapter(row)

    def update_chapter_by_cid(self, cid, data: dict):
        """ 根据章节 id 更新章节信息 """
        condition = f'id={cid} '
        self.db_helper.update(table_name='chapter', data=data, condition=condition)

    def update_chapter_by_bid_cname(self, book_id, display_name, data):
        """ 根据书籍 id 和章节名称更新目录 """
        condition = f'book_id={book_id} and display_name="{display_name}" '
        self.db_helper.update(table_name='chapter', data=data, condition=condition)

    def save_chapter(self, book_id, chapter: Chapter):
        """ 保存章节信息 """
        ch = self.query_chapter_one(book_id=book_id, display_name=chapter.display_name)
        if not ch:
            data = {'book_id': book_id, 'order_id': chapter.order_id,
                    'display_name': chapter.display_name, 'content': chapter.content}
            chapter_id = self.db_helper.insert(table_name='chapter', data=data)
        else: chapter_id = ch.chapter_id
        data = {'chapter_id': chapter_id}
        self.update_catalogue_by_bid_cname(book_id=book_id, chapter_name=chapter.display_name, data=data)
        return chapter_id


def main():
    service = DBService()
    chapters = service.query_chapter_by_bookid(book_id=1)
    print(chapters)


if __name__ == '__main__':
    main()
