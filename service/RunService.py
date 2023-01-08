from spiders.XiaoGeDaSpider import XiaoGeDaSpider


def main():
    spider = XiaoGeDaSpider()
    _, _, books = spider.search(keyword='诛仙')
    print(books)


if __name__ == '__main__':
    main()
