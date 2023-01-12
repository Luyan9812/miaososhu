from service.TaskService import TaskService


task = TaskService()
sites = {
    'https://www.aixs.la/',
    'https://www.81zw.com/',
    'https://www.zwduxs.com/',
    'https://www.biquge7.top/',
    'https://www.biquge365.net/',
    'https://www.xgedaa.com/',
    'https://www.147xs.org/',
    'https://www.xianqihaotianmi.com/'
}


def find_book():
    books = task.search_all(keyword='龙族', author='江南')
    for book in books:
        print(f'《{book.book_name}》"{book.author_name}" 著；首页：{book.url}，封面图：{book.cover_img}', end='\n\n')


def main():
    task.finish_judge()


if __name__ == '__main__':
    main()
