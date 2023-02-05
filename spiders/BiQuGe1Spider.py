import base.AgentInfo as Agent

from model.Book import Book
from urllib.parse import urljoin
from model.Chapter import Chapter
from model.Catalogue import Catalogue
from parsel.selector import Selector
from base.Exceptions import self_catch
from base.BaseRequestsSpider import BaseRequestsSpider


class BiQuGe1Spider(BaseRequestsSpider):
    """
    https://www.biquge7.top/
    搜索无限制
    """

    def __init__(self):
        super().__init__()
        self.tag = 'spiders.BiQuGe1.BiQuGe1'
        self.img_tag = 'spiders.BiQuGe1.BiQuGe1_img'

        self.hot_url = 'https://www.biquge7.top/'
        self.base_url = 'https://www.biquge7.top/'
        self.search_url = 'https://www.biquge7.top/search'

    def headers_b(self):
        headers = {
            'User-Agent': Agent.USER_AGENT,
            'Cookie': Agent.cookies[self.img_tag],
            'referer': 'https://www.biquge7.top/'
        }
        return headers

    def get_search_dict(self, keyword, page=1):
        """ 获取搜索键值对 """
        return {"keyword": keyword, 'page': page}

    @self_catch
    def search(self, keyword: str, page=1):
        """ 搜索书籍 """
        return self.search_get(keyword=keyword, page=page)

    def _parse_hot_list(self, html: str):
        """ 从界面里解析出所有的书本信息 """
        selector = Selector(html)
        books = []
        for box in selector.xpath('//div[@class="tui_1_item"]'):
            cover_img = box.xpath('.//img/@src').get()
            item = box.xpath('./div[@class="item_title"]')
            info = item.xpath('./p/text()').get()
            title = item.xpath('./div')
            book_name = ''.join(title.xpath('./a//text()').getall())
            url = title.xpath('./a/@href').get()
            author_name = title.xpath('./span/text()').get()
            books.append(Book(book_name=book_name, author_name=author_name,
                              update_time='', book_type='', info=info, finish_status=-1,
                              url=urljoin(self.base_url, url), cover_img=cover_img))
        return books

    def _parse_search_page(self, html: str):
        """ 解析搜索界面的书籍、当前页数和总页数 """
        selector = Selector(html)
        books = self._parse_hot_list(html)
        number = selector.xpath('//div[@class="page"]/text()').getall()
        number = list(filter(lambda x: x, map(lambda x: x.strip(), number)))
        current_page, total_page = number[0].split('/', maxsplit=1)
        return current_page, total_page, books

    def _parse_book_index(self, html: str):
        """ 解析某本书的首页 """
        selector = Selector(html)
        detail = selector.xpath('//div[@class="detail"]')
        info = detail.xpath('./p[1]/text()').get()
        cover_img = detail.xpath('.//img/@src').get()
        tits = detail.xpath('.//div[@class="tits"]')
        book_name = tits.xpath('.//strong/text()').get()
        author_name = tits.xpath('./div[@class="up"]/span[1]/text()').get().replace('作者：', '')
        finish = tits.xpath('./div[@class="up"]/span[2]/text()').get().replace('状态：', '')
        finish_status = 1 if finish == '完结' else 0
        update_time = tits.xpath('./div[@class="up"]/span[3]/span/text()').get()
        book_type = selector.xpath('//div[@class="navi"]/div/a[2]/text()').get()
        catalogue = []
        for li in selector.xpath('//div[@class="list"]/ul/li'):
            href = urljoin(self.base_url, li.xpath('./a/@href').get())
            ch_name = li.xpath('./a/text()').get()
            catalogue.append(Catalogue(chapter_name=ch_name, chapter_url=href))
        book = Book(book_name=book_name, author_name=author_name, update_time=update_time,
                    book_type=book_type, info=info, finish_status=finish_status, url='', cover_img=cover_img)
        book.catalogue = catalogue
        book.total_chapter = len(catalogue)
        return book

    def _parse_chapter(self, html):
        """ 解析某章节内容 """
        selector = Selector(html)
        display_name = selector.xpath('//h1[@class="list_tit"]/text()').get()
        content = selector.xpath('//div[@class="text"]/text()').getall()
        content = '\n\n'.join(filter(lambda x: x, map(lambda x: x.strip(), content)))
        return Chapter(display_name=display_name, content=content, url='')


def main():
    spider = BiQuGe1Spider()

    # 《第一序列》
    book = spider.scrape_book_index('https://www.biquge7.top/49918')

    spider.scrape_full_book(book, need_save=True)


if __name__ == '__main__':
    main()
