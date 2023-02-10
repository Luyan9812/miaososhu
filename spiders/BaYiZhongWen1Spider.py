import math

from model.Book import Book
from urllib.parse import urljoin
from model.Chapter import Chapter
from model.Catalogue import Catalogue
from parsel.selector import Selector
from base.Exceptions import self_catch
from base.BaseRequestsSpider import BaseRequestsSpider


class BaYiZhongWen1Spider(BaseRequestsSpider):
    """
    https://www.81zw.com/
    搜索无限制、响应速度很慢
    """

    def __init__(self):
        super().__init__()
        self.hot_url = 'https://www.81zw.com/'
        self.base_url = 'https://www.81zw.com/'
        self.search_url = 'https://www.81zw.com/search.php'

        self.fetch_interval = 100
        self.tag = 'spiders.BaYiZhongWenSpider.BaYiZhongWen'

    def get_search_dict(self, keyword, page=1):
        """ 获取搜索键值对 """
        return {"keyword": keyword, 'page': page}

    @self_catch
    def search(self, keyword: str, page=1):
        """ 搜索书籍 """
        return self.search_get(keyword=keyword, page=page)

    def _parse_hot_list(self, html):
        """ 解析热文书籍 """
        selector = Selector(html)
        books = []
        for box in selector.xpath('//div[@class="item"] | //div[@class="top"]'):
            info = box.xpath('.//dd/text()').get()
            cover_img = box.xpath('.//img/@src').get()
            cover_img = urljoin(self.base_url, cover_img)
            dt = box.xpath('.//dt')
            author_name = dt.xpath('./span/text()').get()
            if author_name is None: author_name = ''
            book_name = dt.xpath('./a/text()').get()
            url = urljoin(self.base_url, dt.xpath('./a/@href').get())
            books.append(Book(book_name=book_name, author_name=author_name,
                              update_time='', book_type='', info=info, finish_status=-1,
                              url=url, cover_img=cover_img))
        return books

    def _parse_search_page(self, html):
        """ 解析搜索界面的书籍、当前页数和总页数 """
        selector = Selector(html)
        books = []
        for box in selector.xpath('//div[@class="result-item result-game-item"]'):
            cover_img = box.xpath('.//img/@src').get()
            cover_img = urljoin(self.base_url, cover_img)
            book_name = box.xpath('.//h3/a/text()').get()
            url = urljoin(self.base_url, box.xpath('.//h3/a/@href').get())
            info = box.xpath('.//p[@class="result-game-item-desc"]/text()').get()
            author_name, book_type, update_time = '', '', ''
            for i, p in enumerate(box.xpath('.//p[@class="result-game-item-info-tag"]')):
                string = p.xpath('./span[2]/text()').get()
                if i == 0: author_name = string
                elif i == 1: book_type = string
                elif i == 2: update_time = string
            books.append(Book(book_name=book_name, author_name=author_name,
                              update_time=update_time, book_type=book_type,
                              info=info, finish_status=-1, url=url, cover_img=cover_img))
        js = selector.xpath('//body/script[last()]/text()').get()
        count, limit, curr = js.strip().split(',')[1: 4]
        curr = int(curr.replace('curr:', '').replace('"', '').strip())
        count = int(count.replace('count:', '').replace('"', '').strip())
        limit = int(limit.replace('limit:', '').replace('"', '').strip())
        current_page = curr
        total_page = math.ceil(count / limit)
        return current_page, total_page, books

    def _parse_book_index(self, html):
        """ 解析某本书的首页 """
        selector = Selector(html)
        cover_img = selector.xpath('//div[@id="fmimg"]/img/@src').get()
        cover_img = urljoin(self.base_url, cover_img)
        div_info = selector.xpath('//div[@id="info"]')
        book_name = div_info.xpath('./h1/text()').get()
        author_name = div_info.xpath('./p[1]/text()').get()
        author_name = author_name.split('：', maxsplit=1)[1]
        finish = div_info.xpath('./p[2]/text()').get()
        finish = finish.split('：', maxsplit=1)[1].strip().replace(',', '')
        finish_status = 1 if finish == '完本' else 0
        update_time = div_info.xpath('./p[3]/text()').get().replace('最后更新：', '')
        info = selector.xpath('//div[@id="intro"]/p[1]/text()').get()
        book_type = selector.xpath('//div[@class="con_top"]/a[2]/text()').get()
        catalogue = []
        for dd in selector.xpath('//div[@id="list"]/dl/dd'):
            href = dd.xpath('./a/@href').get()
            ch_name = dd.xpath('./a/text()').get()
            if ch_name is None: continue
            catalogue.append(Catalogue(chapter_name=ch_name, chapter_url=urljoin(self.base_url, href)))
        book = Book(book_name=book_name, author_name=author_name, update_time=update_time,
                    book_type=book_type, info=info, finish_status=finish_status, url='', cover_img=cover_img)
        book.catalogue = catalogue
        book.total_chapter = len(catalogue)
        return book

    def _parse_chapter(self, html):
        """ 解析章节内容 """
        selector = Selector(html)
        content = selector.xpath('//div[@id="content"]/text()').getall()
        display_name = selector.xpath('//div[@class="bookname"]/h1/text()').get()
        content = '\n\n'.join(filter(lambda x: x, map(lambda x: x.strip(), content)))
        idx = content.rfind('网页版章节内容慢，请下载爱阅小说app阅读最新内容')
        if idx >= 0:
            content = content[0: idx]
        return Chapter(display_name=display_name, content=content, url='')


def main():
    spider = BaYiZhongWen1Spider()

    # 《恶魔法则》
    book = spider.scrape_book_index('https://www.81zw.com/book/17326/')

    spider.scrape_full_book(book, need_save=True)


if __name__ == '__main__':
    main()
