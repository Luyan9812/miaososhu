from service.TaskService import TaskService


def main():
    """ 执行函数 """
    task = TaskService()
    urls = [
        'https://www.biquge7.top/50760',
    ]
    task.scrape_book(urls=urls)


if __name__ == '__main__':
    main()
