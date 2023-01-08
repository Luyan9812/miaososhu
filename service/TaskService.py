import requests

from service.DBService import DBService

from spiders.BiQuGe1Spider import BiQuGe1Spider
from spiders.BiQuGe2Spider import BiQuGe2Spider
from spiders.XiaoGeDaSpider import XiaoGeDaSpider
from spiders.XiaoShuo147Spider import XiaoShuo147Spider
from spiders.BaYiZhongWen1Spider import BaYiZhongWen1Spider
from spiders.BaYiZhongWen2Spider import BaYiZhongWen2Spider


class TaskService(object):
    """ 封装某些任务 """

    def __init__(self):
        self.db_service = DBService()
        self.spiders = {
            'www.biquge7.top': BiQuGe1Spider(),
            'www.biquge365.net': BiQuGe2Spider(),
            'www.81zw.com': BaYiZhongWen1Spider(),
            'www.zwduxs.com': BaYiZhongWen2Spider(),
            'www.147xs.org': XiaoShuo147Spider(),
            'www.xgedaa.com': XiaoGeDaSpider()
        }

    def chose_spider(self, url: str):
        """ 根据 url 选择合适的爬虫 """
        for k in self.spiders:
            if k in url: return self.spiders[k]
        return None

    def content_fix_81zw(self):
        """ 删除 @BaYiZhongWen1Spider 爬取的小说中废话部分 """
        baseurl = 'https://www.81zw.com'
        for book in self.db_service.query_book_by_website(baseurl=baseurl):
            print(book.book_name)
            for chapter in self.db_service.query_chapter_by_bookid_yield(book_id=book.book_id):
                content = chapter.content
                idx = content.rfind('网页版章节内容慢，请下载爱阅小说app阅读最新内容')
                if idx < 0: continue
                content = content[0: idx]
                chapter.content = content
                self.db_service.update_chapter_by_cid(cid=chapter.chapter_id, data=chapter.get_db_dict())
                print('\t' + chapter.display_name)

    def finish_judge(self, is_finish=0):
        """ 判断未完结书籍是否真的未完结 """
        ids = []
        for book in self.db_service.query_book_by_finish_status(is_finish=is_finish):
            if book is None:
                print('GET None')
                continue
            print(book.book_name)
            print('\t', '\n\t'.join(list(book.catalogue.keys())[-10:]))
            answer = input(f'《{book.book_name}》{"未" if is_finish else "已"}完结：')
            if answer == '1': ids.append(book.book_id)
        for book_id in ids:
            self.db_service.update_book_by_id(book_id=book_id, data={'finish_status': 1 - is_finish})

    def update_books(self):
        """ 更新数据库里面的书 """
        for book in self.db_service.query_book_by_finish_status(is_finish=0):
            spider = self.chose_spider(book.url)
            book = spider.scrape_book_index(url=book.url)
            spider.scrape_full_book(book=book, need_save=True)

    def scrape_book(self, url_dict: dict):
        """ 提前找好网址，然后一个个爬取 """
        q_list = []
        p_list = list(url_dict.values())
        while True:
            can_break = True
            for url in p_list:
                try:
                    if not url: continue
                    spider = self.chose_spider(url)
                    if spider is None: continue
                    book = spider.scrape_book_index(url=url)
                    spider.scrape_full_book(book=book, need_save=True)
                except requests.RequestException:
                    can_break = False
                    q_list.append(url)
            if can_break: break
            p_list.clear()
            p_list.extend(q_list)
            q_list.clear()


def _generate_download_dict():
    urls = [
        'https://www.147xs.org/book/3290/',
        'https://www.zwduxs.com/23_23350/',
        'https://www.147xs.org/book/8141/',
        'https://www.biquge7.top/49911',
        'https://www.zwduxs.com/39_39030/',
        'https://www.biquge7.top/49909',
    ]
    download_dict = {}
    for url in urls:
        spider = task.chose_spider(url=url)
        book = spider.scrape_book_index(url=url)
        download_dict[book.book_name] = url
    print(download_dict)


def main():
    url_dict = {
        '校园寻美录全文阅读': 'https://www.xgedaa.com/a49789/',
        '校花的贴身保镖': 'https://www.147xs.org/book/3290/',
        '终极教师': 'https://www.147xs.org/book/8141/',
        '极品修真强少': 'https://www.zwduxs.com/39_39030/',
        '校花的贴身高手': 'https://www.biquge7.top/49909'
    }
    # _generate_download_dict()
    task.scrape_book(url_dict=url_dict)


if __name__ == '__main__':
    task = TaskService()
    main()
