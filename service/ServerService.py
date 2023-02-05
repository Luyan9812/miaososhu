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


dbService = DBService()

spiders = {
    'www.biquge7.top': BiQuGe1Spider(),
    'www.zwduxs.com': BaYiZhongWen2Spider(),
    'www.147xs.org': XiaoShuo147Spider(),
    'www.xgedaa.com': XiaoGeDaSpider(),
    'www.biquge365.net': BiQuGe2Spider(),
    'www.aixs.la': AixsSpider(),
    'www.xianqihaotianmi.com': YanQingXiaoShuoSpider(),
    'www.81zw.com': BaYiZhongWen1Spider(),
}


def get_date():
    now = datetime.now()
    return f'{now.year}-{now.month}-{now.day}'


def get_self_recommends():
    """ 获取本站当日的推荐书籍 """
    # 先从推荐表里查
    books = []
    date = get_date()
    book_ids = dbService.query_commend_by_date(recommend_date=f"'{date}'", resource=0)
    if not book_ids:
        all_ids = list(map(lambda x: x[0], dbService.query_all_books_id()))
        book_ids.extend(random.sample(all_ids, 12))
        for book_id in book_ids:
            dbService.save_commend(book_id=book_id, recommend_date=date, resource=0)
    for book_id in book_ids:
        books.append(dbService.query_book_by_id(book_id=book_id))
    return books


def get_other_recommends():
    """ 获取外站当日的推荐书籍 """
    books = []
    date = get_date()
    book_ids = dbService.query_commend_by_date(recommend_date=f"'{date}'", resource=1)
    if not book_ids:
        for spider in spiders.values():
            bs = spider.hot_list()
            if bs: books.extend(bs)
        books = list(filter(lambda x: x.author_name, books))
        bt = []
        for book in books:
            book_id, save_success = dbService.save_book(book=book)
            if save_success:
                bt.append(book)
                dbService.save_commend(book_id=book_id, recommend_date=date, resource=1)
        books = bt
    else:
        for book_id in book_ids:
            books.append(dbService.query_book_by_id(book_id=book_id))
    return books


def main():
    get_other_recommends()


if __name__ == '__main__':
    main()
