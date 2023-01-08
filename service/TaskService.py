from service.DBService import DBService
from spiders.BiQuGe1Spider import BiQuGe1Spider
from spiders.BiQuGe2Spider import BiQuGe2Spider
from spiders.XiaoShuo147Spider import XiaoShuo147Spider
from spiders.BaYiZhongWen1Spider import BaYiZhongWen1Spider
from spiders.BaYiZhongWen2Spider import BaYiZhongWen2Spider


class TaskService(object):
    """ 封装某些任务 """

    def __init__(self):
        self.db_service = DBService()
        self.spiders = {
            'https://www.biquge7.top': BiQuGe1Spider(),
            'https://www.biquge365.net': BiQuGe2Spider(),
            'https://www.81zw.com': BaYiZhongWen1Spider(),
            'https://www.zwduxs.com': BaYiZhongWen2Spider(),
            'https://www.147xs.org': XiaoShuo147Spider()
        }

    def __chose_spider(self, url: str):
        """ 根据 url 选择合适的爬虫 """
        for k in self.spiders:
            if url.startswith(k): return self.spiders[k]
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

    def finish_judge(self):
        """ 判断未完结书籍是否真的未完结 """
        ids = []
        is_finish = 0
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
            spider = self.__chose_spider(book.url)
            book = spider.scrape_book_index(url=book.url)
            spider.scrape_full_book(book=book, need_save=True)

    def scrape_book(self, urls):
        """ 提前找好网址，然后一个个爬取 """
        for url in urls:
            spider = self.__chose_spider(url)
            if spider is None: continue
            book = spider.scrape_book_index(url=url)
            spider.scrape_full_book(book=book, need_save=True)


def main():
    task = TaskService()
    task.finish_judge()


if __name__ == '__main__':
    main()
