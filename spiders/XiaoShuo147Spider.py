import base.AgentInfo as Agent

from model.Book import Book
from urllib.parse import urljoin
from model.Chapter import Chapter
from parsel.selector import Selector
from base.Exceptions import self_catch
from base.BaseRequestsSpider import BaseRequestsSpider


class XiaoShuo147Spider(BaseRequestsSpider):
    """
    https://www.147xs.org/
    搜索无限制
    """

    def __init__(self):
        super().__init__()
        self.hot_url = 'https://www.147xs.org/'
        self.base_url = 'https://www.147xs.org/'
        self.search_url = 'https://www.147xs.org/search.php'

        self.tag = 'spiders.XiaoShuo147Spider.XiaoShuo147'

    def headers(self):
        """ 网站请求头的封装 """
        return {'User-Agent': Agent.USER_AGENT, 'referer': self.base_url}

    @self_catch
    def search(self, keyword: str, page=1):
        data = {'keyword': keyword}
        html = self.fetch_post(url=self.search_url, data=data)
        current_page, total_page, books = self._parse_search_page(html)
        return current_page, total_page, books

    def _parse_hot_list(self, html):
        """ 解析热文书籍 """
        selector = Selector(html)
        books = []
        for box in selector.xpath('//div[@class="item"] | //div[@class="top"]'):
            info = box.xpath('.//dd/text()').get()
            cover_img = urljoin(self.base_url, box.xpath('.//img/@src').get())
            dt = box.xpath('.//dt')
            book_name = dt.xpath('./a/text()').get()
            url = urljoin(self.base_url, dt.xpath('./a/@href').get())
            author_name = dt.xpath('./span/text()').get()
            if author_name is None:
                author_name = dt.xpath('./text()').get()[1:]
            books.append(Book(book_name=book_name, author_name=author_name,
                              update_time='', book_type='', info=info, finish_status=-1,
                              url=url, cover_img=cover_img))
        return books

    def _parse_search_page(self, html):
        """ 解析搜索界面的书籍、当前页数和总页数 """
        selector = Selector(html)
        books = []
        for tr in selector.xpath('//tbody[@id="bookcase_list"]/tr'):
            book_type = tr.xpath('./td[1]/text()').get()
            url = tr.xpath('./td[2]/a/@href').get()
            book_name = tr.xpath('./td[2]/a//text()').getall()
            book_name = ''.join(map(lambda x: x.strip(), book_name))
            author_name = tr.xpath('./td[4]/text()').get()
            update_time = tr.xpath('./td[5]/text()').get() + ' 00:00:00'
            finish = tr.xpath('./td[6]/text()').get().strip()
            finish_status = 1 if finish == '完本' else 0
            books.append(Book(book_name=book_name, author_name=author_name, update_time=update_time,
                              book_type=book_type, info='', finish_status=finish_status, url=url, cover_img=''))
        return 1, 1, books

    def _parse_book_index(self, html):
        """ 解析某本书的首页 """
        selector = Selector(html)
        div_info = selector.xpath('//div[@id="info"]')
        book_name = div_info.xpath('./h1/text()').get()
        author_name = div_info.xpath('./p[1]/text()').get()
        author_name = author_name.split('：', maxsplit=1)[1]
        update_time = div_info.xpath('./p[3]/text()').get()
        update_time = update_time.split('：', maxsplit=1)[1]
        info = selector.xpath('//div[@id="intro"]/text()').get()
        finish = selector.xpath('//div[@id="fmimg"]/span/@class').get()
        finish_status = 1 if finish == 'a' else 0
        book_type = selector.xpath('//div[@class="con_top"]/a[2]/text()').get()
        cover_img = urljoin(self.base_url, selector.xpath('//div[@id="fmimg"]/img/@src').get())
        catalogue = {}
        for dd in selector.xpath('//div[@id="list"]/dl/dd'):
            a = dd.xpath('./a')
            ch_name = a.xpath('./text()').get()
            href = urljoin(self.base_url, a.xpath('./@href').get())
            catalogue[ch_name] = href
        book = Book(book_name=book_name, author_name=author_name, update_time=update_time,
                    book_type=book_type, info=info, finish_status=finish_status, url='', cover_img=cover_img)
        book.catalogue = catalogue
        book.total_chapter = len(catalogue)
        return book

    def _parse_chapter(self, html):
        """ 解析某章节内容 """
        selector = Selector(html)
        content = selector.xpath('//div[@id="content"]//text()').getall()
        display_name = selector.xpath('//div[@class="bookname"]/h1/text()').get()
        content = '\n\n'.join(filter(lambda x: x, map(lambda x: x.strip(), content)))
        return Chapter(display_name=display_name, content=content, url='')


def main():
    spider = XiaoShuo147Spider()

    # 《我的绝色总裁老婆》
    book = spider.scrape_book_index(url='https://www.147xs.org/book/92279/')

    spider.scrape_full_book(book=book, need_save=True)


if __name__ == '__main__':
    main()
