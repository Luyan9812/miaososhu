import time
import requests
import multiprocessing

from environs import Env
from server.servers import app
from service.TaskService import TaskService


def server():
    """ 服务器任务 """
    env = Env()
    env.read_env()
    host = env.str('HOST')
    port = env.int('PORT')
    app.run(host=host, port=port)


def spider():
    """ 爬虫任务 """
    while True:
        service = TaskService()
        item = service.db_service.query_download_item_by_state(download_state=0)
        if not item:
            print('哎呀，爬虫无事可做')
            time.sleep(30)
            continue
        try:
            item.download_state = 1
            service.db_service.update_download_item_by_id(download_item=item)

            service.scrape_a_book(url=item.url)

            item.download_state = 2
            service.db_service.update_download_item_by_id(download_item=item)
        except requests.RequestException as e:
            item.download_state = -1
            service.db_service.update_download_item_by_id(download_item=item)
            print(f'Fetch {item.url} failed with code: ', e.errno)


def main():
    """ 执行函数 """
    server_process, spider_process = None, None
    try:
        server_process = multiprocessing.Process(target=server)
        spider_process = multiprocessing.Process(target=spider)
        server_process.start()
        spider_process.start()
        server_process.join()
        spider_process.join()
    except KeyboardInterrupt:
        if server_process: server_process.terminate()
        if spider_process: spider_process.terminate()


if __name__ == '__main__':
    main()
