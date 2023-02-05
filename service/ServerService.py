import random

from datetime import datetime
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


class ServerService(object):
    """ 专门处理服务器相关业务逻辑 """

    def __init__(self):
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
            all_ids = list(map(lambda x: x[0], self.dbService.query_all_books_id()))
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
                if bs: books.extend(bs)
            books = list(filter(lambda x: x.author_name, books))
            bt = []
            for book in books:
                book_id, save_success = self.dbService.save_book(book=book)
                if save_success:
                    bt.append(book)
                    self.dbService.save_commend(book_id=book_id, recommend_date=date, resource=1)
            books = bt
        else:
            for book_id in book_ids:
                books.append(self.dbService.query_book_by_id(book_id=book_id))
        return books


def main():
    service = ServerService()
    service.get_other_recommends()


if __name__ == '__main__':
    main()
