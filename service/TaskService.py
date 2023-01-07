from service.DBService import DBService
from spiders.BiQuGe1Spider import BiQuGe1Spider
from spiders.BiQuGe2Spider import BiQuGe2Spider
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
            'https://www.zwduxs.com': BaYiZhongWen2Spider()
        }

    def __chose_spider(self, url):
        """ 根据 url 选择合适的爬虫 """
        for k in self.spiders:
            if url.startswith(k): return self.spiders[k]
        return self.spiders['https://www.biquge7.top']

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

    def update_books(self):
        """ 更新数据库里面的书 """
        for book in self.db_service.query_book_by_finish_status(is_finish=0):
            spider = self.__chose_spider(book.url)
            book = spider.scrape_book_index(url=book.url)
            spider.scrape_full_book(book=book, need_save=True)

    def scrape_book(self):
        """ 提前找好网址，然后一个个爬取 """
        urls = [
            'https://www.zwduxs.com/26_26024/',
            'https://www.biquge365.net/newbook/63611/',
            'https://www.biquge7.top/34959'
        ]
        for url in urls:
            spider = self.__chose_spider(url)
            book = spider.scrape_book_index(url=url)
            spider.scrape_full_book(book=book, need_save=True)


def main():
    task = TaskService()
    task.scrape_book()


if __name__ == '__main__':
    main()
