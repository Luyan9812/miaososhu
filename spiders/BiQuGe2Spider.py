from model.Book import Book
from urllib.parse import urljoin
from model.Chapter import Chapter
from parsel.selector import Selector
from base.BaseRequestsSpider import BaseRequestsSpider


class BiQuGe2Spider(BaseRequestsSpider):
    """
    https://www.biquge365.net/
    搜索限制：至少两个字符、间隔 15s
    """

    def __init__(self):
        super().__init__()
        self.fetch_interval = 50
        self.tag = 'spiders.BiQuGe2Spider.BiQuGe2'

        self.hot_url = 'https://www.biquge365.net/'
        self.base_url = 'https://www.biquge365.net/'
        self.search_url = 'https://www.biquge365.net/s.php'

    def get_search_dict(self, keyword, page=1):
        """ 获取搜索键值对 """
        return {'type': 'articlename', 's': keyword}

    def _parse_hot_list(self, html: str):
        """ 从界面里解析出所有的书本信息 """
        selector = Selector(html)
        books = []
        for li in selector.xpath('//ul[@class="qiangtui"]/li'):
            info = li.xpath('./p[2]/text()').get()
            cover_img = li.xpath('.//img/@src').get()
            book_name = li.xpath('./h3/a/text()').get()
            cover_img = urljoin(self.base_url, cover_img)
            url = urljoin(self.base_url, li.xpath('./h3/a/@href').get())
            books.append(Book(book_name=book_name, author_name='', update_time='',
                              book_type='', info=info, finish_status=-1, url=url, cover_img=cover_img))
        return books

    def _parse_search_page(self, html: str):
        """ 解析搜索界面的书籍、当前页数和总页数 """
        selector = Selector(html)
        books = []
        for li in selector.xpath('//ul[@class="search"]/li[position()>1]'):
            book_name = li.xpath('./span[2]/a/text()').get()
            update_time = li.xpath('./span[5]/text()').get()
            author_name = li.xpath('./span[4]/a/text()').get()
            url = urljoin(self.base_url, li.xpath('./span[2]/a/@href').get())
            book_type = li.xpath('./span[1]/a/text()').get().replace('[', '').replace(']', '')
            books.append(Book(book_name=book_name, author_name=author_name, update_time=update_time,
                              book_type=book_type, info='', finish_status=-1, url=url, cover_img=''))
        return 1, 1, books

    def _parse_book_index(self, html: str):
        """ 解析某本书的首页 """
        selector = Selector(html)
        cover_img = selector.xpath('//div[@class="zhutu"]/img/@src').get()
        cover_img = urljoin(self.base_url, cover_img)
        xin_xi = selector.xpath('//div[@class="xinxi"]')
        author_name = xin_xi.xpath('./span[1]/a/text()').get()
        book_type = xin_xi.xpath('./span[2]/text()').get().replace('类型：', '')
        finish = xin_xi.xpath('./span[3]/text()').get().replace('状态：', '')
        finish_status = 1 if finish == '已完结' else 0
        update_time = xin_xi.xpath('./span[7]/text()').get().replace('更新时间：', '')
        info = xin_xi.xpath('./div/text()').get().replace('简介：', '')
        book_name = selector.xpath('//div[@class="right_border"]/h1/text()').get()
        book = Book(book_name=book_name, author_name=author_name, update_time=update_time,
                    book_type=book_type, info=info, finish_status=finish_status, url='', cover_img=cover_img)
        catalogue = {}
        for li in selector.xpath('//div[@class="border"]/ul/li'):
            ch_name = li.xpath('./a/text()').get()
            href = urljoin(self.base_url, li.xpath('./a/@href').get())
            catalogue[ch_name] = href
        book.catalogue = catalogue
        book.total_chapter = len(catalogue)
        return book

    def _parse_chapter(self, html):
        """ 解析某章节内容 """
        selector = Selector(html)
        display_name = selector.xpath('//div[@id="neirong"]/h1/text()').get()
        content = selector.xpath('//div[@id="txt"]/text()').getall()
        content = '\n\n'.join(list(filter(lambda x: x, list(map(lambda x: x.strip(), content)))))
        return Chapter(display_name=display_name, content=content, url='')


def main():
    spider = BiQuGe2Spider()

    # 《异世之风流大法师》
    book = spider.scrape_book_index('https://www.biquge365.net/newbook/02645/')

    spider.scrape_full_book(book, need_save=True)


if __name__ == '__main__':
    main()
