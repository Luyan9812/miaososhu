import json
import math

from final import RESOURCE_DIR as RES
from service.DBService import DBService
from service.ServerService import ServerService
from flask import Flask, render_template, request, session

app = Flask(__name__)


@app.route('/index')
def index():
    """ 首页 """
    service = ServerService()
    self_books = service.get_self_recommends()
    line_items = [3] * (len(self_books) // 3)
    if len(self_books) % 3: line_items.append(len(self_books) % 3)
    render_dict = {
        'res': RES,
        'line_items': line_items,
        'self_books': self_books
    }
    return render_template('index.html', **render_dict)


@app.route('/catalogue/<int:book_id>')
def catalogue(book_id):
    """ 小说目录页面 """
    service = DBService()
    book = service.query_book_by_id(book_id=book_id, need_catalogue=True)
    render_dict = {
        'res': RES,
        'book': book,
        'lines': math.ceil(len(book.catalogue) / 4),
        'last_items': len(book.catalogue) % 4 if len(book.catalogue) % 4 else 4,
        'latest_chapter_id': book.catalogue[-1].chapter_id,
        'latest_chapter_name': book.catalogue[-1].chapter_name
    }
    return render_template('catalogue.html', **render_dict)


@app.route('/chapter/<int:chapter_id>')
def chapter(chapter_id):
    """ 阅读页面 """
    service = DBService()
    ch = service.query_chapter_by_id(chapter_id=chapter_id)
    book = service.query_book_by_id(book_id=ch.book_id, need_catalogue=True)
    for i, item in enumerate(book.catalogue):
        if item.chapter_id == chapter_id: break
    pre_id = -1 if i == 0 else book.catalogue[i - 1].chapter_id
    after_id = -1 if i == len(book.catalogue) - 1 else book.catalogue[i + 1].chapter_id
    render_dict = {
        'res': RES,
        'chapter': ch,
        'pre_id': pre_id,
        'after_id': after_id,
        'book_id': book.book_id,
        'book_name': book.book_name
    }
    return render_template('reading.html', **render_dict)


@app.route('/search', methods=['POST'])
def search():
    """ 搜索界面 """
    service = ServerService()
    kw = request.form.get('kw')
    search_type = int(request.form.get('type'))
    books = service.search_local(kw=kw, search_type=search_type)
    local_lines = math.ceil(len(books) / 3)
    local_last_n = len(books) % 3 if len(books) % 3 else 3
    render_dict = {
        'kw': kw,
        'res': RES,
        'type': search_type,
        'localBooks': books,
        'localLines': local_lines,
        'localLastN': local_last_n
    }
    return render_template('search.html', **render_dict)


@app.route('/otherRecommend', methods=['POST'])
def other_recommends():
    """ 首页里面请求外站小说接口 """
    service = ServerService()
    books = service.get_other_recommends()
    return json.dumps(list(map(_transform_book, books)), ensure_ascii=False)


@app.route('/otherSearch', methods=['POST'])
def other_search():
    """ 搜索外站小说 """
    service = ServerService()
    kw = request.form.get('kw')
    search_type = int(request.form.get('type'))
    books = service.search_other(kw=kw, search_type=search_type)
    return json.dumps(list(map(_transform_book, books)), ensure_ascii=False)


@app.route('/cloudSave', methods=['POST'])
def cloud_save():
    """ 转存小说到本站 """
    service = ServerService()
    url = request.form.get('url')
    print('转存：', url)
    return '[]'


def _transform_book(book):
    book_map = {
        "book_name": book.book_name,
        "author_name": book.author_name,
        "info": book.info,
        "url": book.url,
        "cover_img": book.cover_img,
        'update_time': book.update_time
    }
    return book_map


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4999)
