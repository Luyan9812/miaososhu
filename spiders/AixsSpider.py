from model.Book import Book
from urllib.parse import urljoin
from model.Chapter import Chapter
from parsel.selector import Selector
from base.BaseRequestsSpider import BaseRequestsSpider


class AixsSpider(BaseRequestsSpider):
    """
    https://www.aixs.la/
    搜索无限制
    """

    def __init__(self):
        super().__init__()
        self.hot_url = 'https://www.aixs.la/'
        self.base_url = 'https://www.aixs.la/'
        self.search_url = 'https://www.aixs.la/search.php'

        self.tag = 'spiders.AixsSpider.AixsSpider'

    def get_search_dict(self, keyword, page=1):
        """ 获取搜索键值对 """
        return {'key': keyword}

    def _parse_hot_list(self, html):
        """ 解析热文书籍 """
        selector = Selector(html)
        books = []
        for dl in selector.xpath('//dl[@class="book-block"]'):
            cover_img = 'https:' + dl.xpath('.//img/@data-original').get()
            info = dl.xpath('.//span[@class="book-info"]/text()').get()
            author_name = dl.xpath('.//span[@class="book-author"]/text()').get().replace('作者：', '')
            book_name = dl.xpath('.//h5/a/text()').get()
            url = urljoin(self.base_url, dl.xpath('.//h5/a/@href').get())
            books.append(Book(book_name=book_name, author_name=author_name,
                              update_time='', book_type='', info=info, finish_status=-1,
                              url=url, cover_img=cover_img))
        return books

    def _parse_search_page(self, html):
        """ 解析搜索界面的书籍、当前页数和总页数 """
        selector = Selector(html)
        books = []
        for dd in selector.xpath('//div[@class="secd-rank-list"]//dd'):
            book_name = dd.xpath('./a/text()').get()
            url = urljoin(self.base_url, dd.xpath('./a/@href').get())
            p = dd.xpath('./p[1]')
            author_name = p.xpath('./a[1]/text()').get()
            book_type = p.xpath('./a[2]/text()').get()
            finish_status = 0 if '连载中' in ''.join(p.xpath('./text()').getall()) else 1
            books.append(Book(book_name=book_name, author_name=author_name, update_time='',
                              book_type=book_type, info='', finish_status=finish_status, url=url, cover_img=''))
        return 1, 1, books

    def _parse_book_index(self, html):
        """ 解析某本书的首页 """
        selector = Selector(html)
        info = selector.xpath('//p[@class="brief_text"]/text()').getall()
        update_time = selector.xpath('//span[@class="updatetime fr"]/text()').get()
        update_time = update_time.replace('更新时间', '').replace(':', '', 1).strip()
        info = '\n'.join(filter(lambda x: x, map(lambda x: x and x.strip(), info)))
        cover_img = 'https:' + selector.xpath('//div[@class="pic fl"]//img/@src').get()
        finish_status = 0 if selector.xpath('//span[@class="fl isfinish"]/text()').get() == '连载中'else 1
        sub_url = urljoin(self.base_url, selector.xpath('//div[@class="tab fl j-content-tab"]/a[2]/@href').get())

        html = self.fetch(url=sub_url)
        selector = Selector(html)
        book_name = selector.xpath('//span[@class="name fl"]/text()').get()
        author_name = selector.xpath('//a[@class="author fl"]/text()').get()
        book_type = selector.xpath('//div[contains(@class, "path")]/a[2]/text()').get()
        catalogue = {}
        div = selector.xpath('//ul[@id="listsss"]/div')
        div.sort(key=lambda x: int(x.xpath('./@data-id').get()))
        for li in div.xpath('./li'):
            ch_name = li.xpath('./a/text()').get()
            href = urljoin(sub_url, li.xpath('./a/@href').get())
            catalogue[ch_name] = href
        book = Book(book_name=book_name, author_name=author_name, update_time=update_time,
                    book_type=book_type, info=info, finish_status=finish_status, url='', cover_img=cover_img)
        book.catalogue = catalogue
        book.total_chapter = len(catalogue)
        return book

    def _parse_chapter(self, html):
        """ 解析某章节内容 """
        selector = Selector(html)
        contents = []
        display_name = selector.xpath('//h2/text()').get()

        dd = selector.xpath('//div[@id="txt"]/dd')
        dd.sort(key=lambda x: int(x.xpath('./@data-id').get()))
        for p in dd.xpath('./p'):
            contents.append(p.xpath('./text()').get())
        content = '\n\n'.join(filter(lambda x: x, map(lambda x: x and x.strip(), contents)))
        return Chapter(display_name=display_name, content=content, url='')


def main():
    spider = AixsSpider()

    # 《诱惑学院之绝色物语》
    book = spider.scrape_book_index('https://www.aixs.la/book/15908.html')

    spider.scrape_full_book(book, need_save=True, force_generate_file=True)


if __name__ == '__main__':
    main()
