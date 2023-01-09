from model.Book import Book
from urllib.parse import urljoin
from model.Chapter import Chapter
from parsel.selector import Selector
from base.BaseRequestsSpider import BaseRequestsSpider


class BaYiZhongWen2Spider(BaseRequestsSpider):
    """
    https://www.zwduxs.com/
    搜索无限制
    """

    def __init__(self):
        super().__init__()
        self.hot_url = 'https://www.zwduxs.com/'
        self.base_url = 'https://www.zwduxs.com/'
        self.search_url = 'https://www.zwduxs.com/modules/article/search.php'

        self.tag = 'spiders.BaYiZhongWen2Spider.BaYiZhongWen2'

    def get_search_dict(self, keyword, page=1):
        """ 获取搜索键值对 """
        return {'searchkey': keyword, 'searchtype': 'articlename'}

    def _parse_hot_list(self, html):
        """ 解析热文书籍 """
        selector = Selector(html)
        books = []
        for box in selector.xpath('//div[@class="item"] | //div[@class="top"]'):
            info = box.xpath('.//dd/text()').get()
            cover_img = box.xpath('.//img/@src').get()
            dt = box.xpath('.//dt')
            author_name = dt.xpath('./span/text()').get()
            if author_name is None: author_name = ''
            book_name = dt.xpath('./a/text()').get()
            url = dt.xpath('./a/@href').get()
            books.append(Book(book_name=book_name, author_name=author_name,
                              update_time='', book_type='', info=info, finish_status=-1,
                              url=url, cover_img=cover_img))
        return books

    def _parse_search_page(self, html):
        """ 解析搜索界面的书籍、当前页数和总页数 """
        selector = Selector(html)
        books = []
        for tr in selector.xpath('//div[@id="content"]//tr[position()>1]'):
            url = tr.xpath('./td[1]/a/@href').get()
            book_name = tr.xpath('./td[1]/a/text()').get()
            author_name = tr.xpath('./td[3]/text()').get()
            update_time = tr.xpath('./td[5]/text()').get()
            finish = tr.xpath('./td[6]/text()').get()
            finish_status = 1 if finish == '全本' else 0
            books.append(Book(book_name=book_name, author_name=author_name, update_time=update_time,
                              book_type='', info='', finish_status=finish_status, url=url, cover_img=''))
        return 1, 1, books

    def _parse_book_index(self, html):
        """ 解析某本书的首页 """
        selector = Selector(html)
        cover_img = selector.xpath('//div[@id="fmimg"]/img/@src').get()
        div_info = selector.xpath('//div[@id="info"]')
        book_name = div_info.xpath('./h1/text()').get()
        author_name = div_info.xpath('./p[1]/text()').get()
        author_name = author_name.split('：', maxsplit=1)[1]
        finish = selector.xpath('//div[@id="fmimg"]/span/@class').get()
        finish_status = 1 if finish == 'a' else 0
        info = selector.xpath('//div[@id="intro"]/p[1]/text()').get()
        book_type = selector.xpath('//div[@class="con_top"]/a[2]/text()').get()
        update_time = div_info.xpath('./p[3]/text()').get().replace('最后更新：', '')
        catalogue = {}
        for dd in selector.xpath('//div[@id="list"]/dl/dd'):
            ch_name = dd.xpath('./a/text()').get()
            href = urljoin(self.base_url, dd.xpath('./a/@href').get())
            catalogue[ch_name] = href
        book = Book(book_name=book_name, author_name=author_name, update_time=update_time,
                    book_type=book_type, info=info, finish_status=finish_status, url='', cover_img=cover_img)
        book.catalogue = catalogue
        book.total_chapter = len(catalogue)
        return book

    def _parse_chapter(self, html):
        """ 解析某章节内容 """
        selector = Selector(html)
        content = selector.xpath('//div[@id="content"]/text()').getall()
        display_name = selector.xpath('//div[@class="bookname"]/h1/text()').get()
        content = '\n\n'.join(filter(lambda x: x, map(lambda x: x.strip(), content)))
        return Chapter(display_name=display_name, content=content, url='')


def main():
    spider = BaYiZhongWen2Spider()

    # 《校花的全能保安》
    book = spider.scrape_book_index('https://www.zwduxs.com/23_23350/')

    spider.scrape_full_book(book, need_save=True, force_generate_file=True)


if __name__ == '__main__':
    main()
