import json
import math

from service.DBService import DBService
from service.ServerService import ServerService
from server.final import RESOURCE_DIR as RES, AUTH_KEY

from flask import Flask
from flask import render_template, request, session, redirect


app = Flask(__name__)
app.secret_key = 'LYLMX5201314'


def auth_judge():
    """ 判断是否鉴权 """
    authcode = session.get(AUTH_KEY)
    if not authcode:
        return redirect('/authority?info=1')
    else:
        service = ServerService()
        row = service.authority_exists(authcode=authcode)
        if not row or row[2] <= 0:
            return redirect('/authority?info=2')
    return None


@app.route('/index')
def index():
    """ 首页 """
    auth = auth_judge()
    if auth is not None: return auth

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
    auth = auth_judge()
    if auth is not None: return auth

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
    auth = auth_judge()
    if auth is not None: return auth

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
    auth = auth_judge()
    if auth is not None: return auth

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


@app.route('/authority')
def authority():
    """ 输入鉴权码界面 """
    info = request.args.get('info')
    if not info: info = ''
    info = '鉴权码已失效' if info == '2' else '访问本站需提供鉴权码'
    render_dict = {
        'res': RES,
        'info': info
    }
    return render_template('authority.html', **render_dict)


@app.route('/login')
def authority_login():
    """ 后台登录界面 """
    render_dict = {
        'res': RES,
    }
    return render_template('authority_login.html', **render_dict)


@app.route('/manager')
def authority_manager():
    """ 后台管理界面 """
    user = session.get('user')
    if not user: return redirect('/login')
    render_dict = {
        'res': RES,
    }
    return render_template('authority_manager.html', **render_dict)


@app.route('/loginValidate', methods=['POST'])
def login_validate():
    """ 登录检验 """
    service = ServerService()
    uname = request.form.get('uname')
    upassword = request.form.get('upassword')
    user = service.dbService.query_user_by_name_password(uname=uname, upassword=upassword)
    if not user: return '用户名或密码错误'
    if user.urole != 1: return '权限不足'
    session['user'] = user.get_dict()
    return 'Success'


@app.route('/validateAuthcode', methods=['POST'])
def validate_authcode():
    """ 验证鉴权码 """
    authcode = request.form.get('authcode')
    if not authcode: return '访问本站需提供鉴权码'
    service = ServerService()
    row = service.authority_exists(authcode=authcode)
    if not row: return '无效鉴权码'
    if row[2] <= 0: return '鉴权码已失效'
    session[AUTH_KEY] = authcode
    return 'Success'


@app.route('/otherRecommend', methods=['POST'])
def other_recommends():
    """ 首页里面请求外站小说接口 """
    auth = auth_judge()
    if auth is not None: return '[]'

    service = ServerService()
    service.decrease_authority(session[AUTH_KEY])
    books = service.get_other_recommends()
    return json.dumps(list(map(_transform_book, books)), ensure_ascii=False)


@app.route('/otherSearch', methods=['POST'])
def other_search():
    """ 搜索外站小说 """
    auth = auth_judge()
    if auth is not None: return '[]'

    service = ServerService()
    service.decrease_authority(session[AUTH_KEY])
    kw = request.form.get('kw')
    search_type = int(request.form.get('type'))
    books = service.search_other(kw=kw, search_type=search_type)
    return json.dumps(list(map(_transform_book, books)), ensure_ascii=False)


@app.route('/cloudSave', methods=['POST'])
def cloud_save():
    """ 转存小说到本站 """
    auth = auth_judge()
    if auth is not None: return '[]'

    service = ServerService()
    service.decrease_authority(session[AUTH_KEY], times=5)
    url = request.form.get('url')
    print('转存：', url)
    service.dbService.save_download_item(url=url, download_state=0)
    return '[]'


def _transform_book(book):
    book_map = {
        "url": book.url,
        "info": book.info,
        "cover_img": book.cover_img,
        "book_name": book.book_name,
        'book_type': book.book_type,
        "author_name": book.author_name,
        'update_time': book.update_time,
    }
    return book_map


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=4999)
