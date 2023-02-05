import json
from final import RESOURCE_DIR as RES
from flask import Flask, render_template
from service.ServerService import ServerService


app = Flask(__name__)


@app.route('/index')
def index():
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


@app.route('/others', methods=['POST'])
def other_novels():
    books_map = []
    service = ServerService()
    books = service.get_other_recommends()
    for book in books:
        books_map.append({"book_name": book.book_name, "author_name": book.author_name,
                          "info": book.info, "url": book.url, "cover_img": book.cover_img})
    return json.dumps(books_map, ensure_ascii=False)


@app.route('/catalogue/<int:book_id>')
def catalogue(book_id):
    service = ServerService()
    book = service.dbService.query_book_by_id(book_id=book_id, need_catalogue=True)
    render_dict = {
        'res': RES,
        'book': book,
        'latest_chapter_name': list(book.catalogue.keys())[-1]
    }

    return render_template('catalogue.html', **render_dict)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4999)
