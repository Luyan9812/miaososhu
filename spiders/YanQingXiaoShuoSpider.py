from model.Book import Book
from urllib.parse import urljoin
from model.Chapter import Chapter
from parsel.selector import Selector
from base.BaseRequestsSpider import BaseRequestsSpider


class YanQingXiaoShuoSpider(BaseRequestsSpider):
    """
    https://www.xianqihaotianmi.com/
    搜索无限制
    """

    def __init__(self):
        super().__init__()
        self.hot_url = 'https://www.xianqihaotianmi.com/'
        self.base_url = 'https://www.xianqihaotianmi.com/'
        self.search_url = 'https://www.xianqihaotianmi.com/modules/article/search.php'

        self.tag = 'spiders.YanQingXiaoShuoSpider.YanQingXiaoShuoSpider'

    def get_search_dict(self, keyword, page=1):
        """ 获取搜索键值对 """
        return {'searchkey': keyword}

    def _parse_hot_list(self, html):
        """ 解析热文书籍 """
        selector = Selector(html)
        books = []
        for div in selector.xpath('//div[@class="media"]'):
            url = div.xpath('.//h4/a/@href').get()
            cover_img = div.xpath('.//img/@src').get()
            book_name = div.xpath('.//h4/a/text()').get()
            info = div.xpath('.//p[last()]/text()').get()
            info = info.strip() if info else ''
            author_name = div.xpath('.//*[@class="book_author"]/a/text()').get()
            books.append(Book(book_name=book_name, author_name=author_name,
                              update_time='', book_type='', info=info, finish_status=-1,
                              url=url, cover_img=cover_img))
        return books

    def _parse_search_page(self, html):
        """ 解析搜索界面的书籍、当前页数和总页数 """
        selector = Selector(html)
        books = []
        for tr in selector.xpath('//tr[position()>1]'):
            url = tr.xpath('./td[2]//a/@href').get()
            book_name = tr.xpath('./td[2]//a/text()').get()
            author_name = tr.xpath('./td[3]//a/text()').get()
            update_time = tr.xpath('./td[4]/p/text()').get()
            y, m, d = update_time.strip().split('-', maxsplit=2)
            update_time = f'20{y}-{m}-{d} 00:00:00'
            finish = tr.xpath('./td[5]/p/text()').get().strip()
            finish_status = 0 if finish == '连载' else 1
            books.append(Book(book_name=book_name, author_name=author_name, update_time=update_time,
                              book_type='', info='', finish_status=finish_status, url=url, cover_img=''))
        return 1, 1, books

    def _parse_book_index(self, html):
        """ 解析某本书的首页 """
        selector = Selector(html)
        book_name = selector.xpath('//h1/text()').get()
        div = selector.xpath('//div[contains(@class, "info3")]')
        update_time = div.xpath('./p[2]/font/text()').get()
        book_type, finish = div.xpath('./p[1]/text()').get().split('/', maxsplit=1)
        finish = finish.strip().replace('写作状态：', '')
        finish_status = 0 if finish == '连载中' else 1
        book_type = book_type.strip().replace('小说类别：', '')
        info = selector.xpath('//div[@class="info2"]//p/text()').get()
        author_name = selector.xpath('//h3/text()').get().replace('作者:', '')
        cover_img = urljoin(self.base_url, selector.xpath('//div[@class="info1"]/img/@src').get())
        catalogue = {}
        for li in selector.xpath('//div[@class="panel-body"]/ul[contains(@class, "list-charts")]//li'):
            ch_name = li.xpath('./a/text()').get()
            href = urljoin(self.base_url, li.xpath('./a/@href').get())
            catalogue[ch_name] = href
        book = Book(book_name=book_name, author_name=author_name, update_time=update_time,
                    book_type=book_type, info=info, finish_status=finish_status, url='', cover_img=cover_img)
        book.catalogue = catalogue
        book.total_chapter = len(catalogue)
        return book

    def _parse_chapter(self, html):
        """ 解析某章节内容 """
        selector = Selector(html)
        display_name = selector.xpath('//div[@class="panel-heading"]/text()').get().strip()
        content = selector.xpath('//div[contains(@class, "content-body")]/text()').getall()
        if ' '.join(content[0].strip().split()) == display_name:
            del content[0]
        content = '\n\n'.join(filter(lambda x: x, map(lambda x: x.strip(), content)))
        return Chapter(display_name=display_name, content=content, url='')


def main():
    spider = YanQingXiaoShuoSpider()

    # 《校花的贴身兵王》
    book = spider.scrape_book_index('https://www.xianqihaotianmi.com/book/6035.html')

    spider.scrape_full_book(book, need_save=True, force_generate_file=True)


if __name__ == '__main__':
    main()
