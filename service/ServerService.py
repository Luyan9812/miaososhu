import random

from datetime import datetime
from model.AuthCode import AuthCode
from service.DBService import DBService
from spiders.AixsSpider import AixsSpider
from spiders.BiQuGe1Spider import BiQuGe1Spider
from spiders.BiQuGe2Spider import BiQuGe2Spider
from spiders.XiaoGeDaSpider import XiaoGeDaSpider
from spiders.XiaoShuo147Spider import XiaoShuo147Spider
from spiders.BaYiZhongWen1Spider import BaYiZhongWen1Spider
from spiders.BaYiZhongWen2Spider import BaYiZhongWen2Spider
from spiders.YanQingXiaoShuoSpider import YanQingXiaoShuoSpider


def get_date():
    now = datetime.now()
    return f'{now.year}-{now.month}-{now.day}'


def get_book_author(kw, search_type):
    book_name = ''
    author_name = ''
    if search_type == 1:
        book_name = kw
    elif search_type == 2:
        author_name = kw
    else:
        book_name, author_name = kw.split('@', maxsplit=1)
    return book_name, author_name


class ServerService(object):
    """ 专门处理服务器相关业务逻辑 """

    def __init__(self):
        self.num_page = 60
        self.dbService = DBService()
        self.spiders = {
            'www.biquge7.top': BiQuGe1Spider(),
            'www.zwduxs.com': BaYiZhongWen2Spider(),
            'www.147xs.org': XiaoShuo147Spider(),
            'www.xgedaa.com': XiaoGeDaSpider(),
            'www.biquge365.net': BiQuGe2Spider(),
            'www.aixs.la': AixsSpider(),
            'www.xianqihaotianmi.com': YanQingXiaoShuoSpider(),
            'www.81zw.com': BaYiZhongWen1Spider(),
        }

    def get_self_recommends(self):
        """ 获取本站当日的推荐书籍 """
        # 先从推荐表里查
        books = []
        date = get_date()
        book_ids = self.dbService.query_commend_by_date(recommend_date=f"'{date}'", resource=0)
        if not book_ids:
            all_ids = list(map(lambda x: x[0], self.dbService.query_all_books_id(con=' AND book_type_id != -1 ')))
            book_ids.extend(random.sample(all_ids, 12))
            for book_id in book_ids:
                self.dbService.save_commend(book_id=book_id, recommend_date=date, resource=0)
        for book_id in book_ids:
            books.append(self.dbService.query_book_by_id(book_id=book_id))
        return books

    def get_other_recommends(self):
        """ 获取外站当日的推荐书籍 """
        books = []
        date = get_date()
        book_ids = self.dbService.query_commend_by_date(recommend_date=f"'{date}'", resource=1)
        if not book_ids:
            for spider in self.spiders.values():
                bs = spider.hot_list()
                if not bs: continue
                bs = list(filter(lambda x: x.author_name, bs))
                books.extend(bs)
                for book in bs:
                    spider.save_cover_img(book)
                    book_id, _ = self.dbService.save_book(book=book)
                    b = self.dbService.query_book_by_id(book_id=book_id)
                    book.book_type = b.book_type
                    self.dbService.save_commend(book_id=book_id, recommend_date=date, resource=1)
        else:
            for book_id in book_ids:
                books.append(self.dbService.query_book_by_id(book_id=book_id))
        return books

    def search_local(self, kw, search_type):
        """ 搜索本地数据 """
        con = ' AND book_type_id != -1 '
        book_name, author_name = get_book_author(kw, search_type)
        if search_type == 1:
            books = self.dbService.query_book_like(kw=book_name, con=con)
        elif search_type == 2:
            books = self.dbService.query_book_by_author_like(author_name=author_name, con=con)
        else:
            books = self.dbService.query_book_by_book_author_like(book_name=book_name, author_name=author_name, con=con)
        for book in books:
            book.precise = len(book_name) / len(book.book_name)
        return sorted(books, key=lambda x: x.precise, reverse=True)

    def search_other(self, kw, search_type):
        """ 搜索外站数据 """
        tb, books = [], []
        book_name, author_name = get_book_author(kw, search_type)
        for spider in self.spiders.values():
            tmp = spider.search(keyword=book_name)
            if tmp: tb.extend(tmp[2])
        for book in tb:
            if search_type == 1:
                if book_name not in book.book_name: continue
                book.precise = len(book_name) / len(book.book_name)
            elif search_type == 2:
                if author_name not in book.author_name: continue
                book.precise = len(author_name) / len(book.author_name)
            else:
                if book_name not in book.book_name or author_name not in book.author_name: continue
                book.precise = len(book_name) / len(book.book_name) + len(author_name) / len(book.author_name)
            books.append(book)
        return sorted(books, key=lambda x: x.precise, reverse=True)

    def authority_exists(self, authcode):
        """ 判断鉴权码是否存在，存在就返回一条记录 """
        return self.dbService.query_authcode_by_code(code=authcode)

    def decrease_authority(self, authcode, times=1):
        """ 将对应鉴权码的有效次数减一 """
        aid, _, valid_times = self.dbService.query_authcode_by_code(code=authcode)
        self.dbService.update_authcode(aid=aid, valid_times=valid_times - times)

    def get_all_authcode(self):
        """ 查询所有鉴权码 """
        rows = self.dbService.query_all_authcode()
        if not rows: return []
        authcode_list = []
        for row in rows:
            aid, authcode, valid_times = row
            authcode_list.append(AuthCode(authcode=authcode, valid_times=valid_times, aid=aid))
        return authcode_list

    def get_local_book_by_page(self, page):
        """ 获取指定页数的本地书籍 """
        condition = f' book_type_id > 0 '
        n = self.num_page
        m = (page - 1) * n
        limit = f' {m}, {n} '
        books = self.dbService.query_book_by_condition(condition=condition, limit=limit)
        return books


def main():
    service = ServerService()
    service.get_other_recommends()


if __name__ == '__main__':
    main()
