from model.Book import Book
from urllib.parse import urljoin
from model.Chapter import Chapter
from parsel.selector import Selector
from base.Exceptions import self_catch
from base.BaseRequestsSpider import BaseRequestsSpider


class XiaoGeDaSpider(BaseRequestsSpider):
    """
    https://www.xgedaa.com/
    搜索无限制
    """

    def __init__(self):
        super().__init__()
        self.hot_url = 'https://www.xgedaa.com/'
        self.base_url = 'https://www.xgedaa.com/'
        self.search_url = 'https://www.xgedaa.com/home/search'

        self.tag = 'spiders.XiaoGeDaSpider.XiaoGeDaSpider'

    def get_search_dict(self, keyword, page=1):
        """ 获取搜索键值对 """
        return {'action': 'search', 'q': keyword}

    @self_catch
    def scrape_chapter(self, chapter_url: str):
        """ 根据链接爬取某一个章节内容 """
        html = self.fetch(chapter_url)
        chapter = self._parse_chapter(html)

        if chapter.display_name.rfind('/') >= 0:
            total_page = int(chapter.display_name.rsplit('/', maxsplit=1)[1].replace(')', '').strip())
            for i in range(total_page - 1):
                sub_url = chapter_url.replace('.html', '') + f'_{i + 1}.html'
                html = self.fetch(sub_url)
                sub_chapter = self._parse_chapter(html)
                chapter.content += sub_chapter.content

        # 爬取的时候输出当前爬哪一章
        print('\t' + chapter.display_name)
        chapter.url = chapter_url
        return chapter

    def _parse_hot_list(self, html):
        """ 解析热文书籍 """
        selector = Selector(html)
        books = []
        for dl in selector.xpath('//div[@class="fengtui"]/dl'):
            info = dl.xpath('.//p/text()').get()
            cover_img = dl.xpath('.//img/@src').get()
            book_name = dl.xpath('.//h3/a/text()').get()
            author_name = dl.xpath('.//span/a/text()').get()
            url = urljoin(self.base_url, dl.xpath('.//h3/a/@href').get())
            books.append(Book(book_name=book_name, author_name=author_name,
                              update_time='', book_type='', info=info, finish_status=-1,
                              url=url, cover_img=cover_img))
        return books

    def _parse_search_page(self, html):
        """ 解析搜索界面的书籍、当前页数和总页数 """
        selector = Selector(html)
        books = []
        for dl in selector.xpath('//div[@class="fengtui fengtui_top cf"]/dl'):
            info = dl.xpath('.//p/text()').get()
            cover_img = dl.xpath('.//img/@src').get()
            book_name = dl.xpath('.//h3/a/text()').get()
            author_name = dl.xpath('.//span/text()').get()
            url = urljoin(self.base_url, dl.xpath('.//h3/a/@href').get())
            books.append(Book(book_name=book_name, author_name=author_name,
                              update_time='', book_type='',
                              info=info, finish_status=-1, url=url, cover_img=cover_img))
        return 1, 1, books

    def _parse_book_index(self, html):
        """ 解析某本书的首页 """
        selector = Selector(html)
        book_name = selector.xpath('//h1/text()').get()
        info = selector.xpath('//div[@class="intro"]/text()').get()
        cover_img = selector.xpath('//div[@class="lf"]/img/@src').get()
        finish = selector.xpath('//div[@class="msg"]/em[2]/text()').get()
        finish_status = 0 if finish.strip() == '状态：连载中' else 1
        author_name = selector.xpath('//div[@class="msg"]/em[1]/a/text()').get()
        book_type = selector.xpath('//div[@class="rt"]/div[2]/a/text()').get().strip()
        update_time = selector.xpath('//div[@class="msg"]/em[3]/text()').get().replace('更新时间：', '')
        catalogue = {}
        for li in selector.xpath('//div[@class="mulu"][2]/ul/li'):
            ch_name = li.xpath('./a/text()').get().strip()
            href = urljoin(self.base_url, li.xpath('./a/@href').get())
            catalogue[ch_name] = urljoin(self.base_url, href)
        book = Book(book_name=book_name, author_name=author_name, update_time=update_time,
                    book_type=book_type, info=info, finish_status=finish_status, url='', cover_img=cover_img)
        book.catalogue = catalogue
        book.total_chapter = len(catalogue)
        return book

    def _parse_chapter(self, html):
        """ 解析章节内容 """
        selector = Selector(html)
        display_name = selector.xpath('//h1/text()').get()
        selector.xpath('//div[@id="content"]//font').drop()
        selector.xpath('//div[@id="content"]//script').drop()
        selector.xpath('//div[@id="content"]//button').drop()
        content = selector.xpath('//div[@id="content"]//text()').getall()
        delete_prefix = ['重大通知', '小疙瘩小说网', '手机支付宝', '阅读模式无法', '-->>', '本章未完，点击']

        content = map(lambda x: x and x.strip(), content)
        content = '\n\n'.join(filter(lambda x: x and not self.__startswith(x, delete_prefix), content))
        return Chapter(display_name=display_name, content=content, url='')

    @staticmethod
    def __startswith(s: str, prefixes):
        """ 判断 s 是否由 prefix 里面元素开头 """
        for p in prefixes:
            if s.startswith(p): return True
        return False


def main():
    spider = XiaoGeDaSpider()

    # 《校园寻美录》
    book = spider.scrape_book_index('https://www.xgedaa.com/a49789/')

    spider.scrape_full_book(book, need_save=True)


if __name__ == '__main__':
    main()
