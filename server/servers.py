import json
import math
import random

from environs import Env
from service.DBService import DBService
from service.ServerService import ServerService
from server.final import RESOURCE_DIR as RES, AUTH_KEY

from flask import Flask
from flask import render_template, request, session, redirect


env = Env()
env.read_env()
host = env.str('HOST')
port = env.int('PORT')
secret_key = env.str('SECRET_KEY')

app = Flask(__name__)
app.secret_key = secret_key


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


def get_random_authcode():
    """ 生成随机鉴权码 """
    key = 'ABCDEFGHIJKLMNOPQRStUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    random_str = ''.join(random.sample(list(key), 6))
    return random_str


@app.before_request
def flt():
    """ 静态资源访问需要鉴权码 """
    path = request.path
    #if 'covers' not in path and 'epub' not in path: return None
    if 'epub' not in path: return None
    auth = auth_judge()
    if auth is not None: return auth


@app.route('/')
def index2():
    return redirect('/index')


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


@app.route('/local')
def local_index():
    """ 本站首页 """
    auth = auth_judge()
    if auth is not None: return auth

    service = ServerService()
    page = request.args.get('page')
    page = 1 if not page else int(page)
    books = service.get_local_book_by_page(page=page)
    total = service.dbService.count_books_by_condition(condition=' book_type_id > 0 ')
    total = math.ceil(total / service.num_page)
    line_items = [3] * (len(books) // 3)
    if len(books) % 3: line_items.append(len(books) % 3)
    render_dict = {
        'res': RES,
        'line_items': line_items,
        'books': books,
        'total': total,
        'page': page
    }
    return render_template('local_index.html', **render_dict)


@app.route('/catalogue/<int:book_id>')
def catalogue(book_id):
    """ 小说目录页面 """
    auth = auth_judge()
    if auth is not None: return auth

    service = DBService()
    user = session.get('user')
    book = service.query_book_by_id(book_id=book_id, need_catalogue=True)
    render_dict = {
        'res': RES,
        'book': book,
        'lines': math.ceil(len(book.catalogue) / 3),
        'last_items': len(book.catalogue) % 3 if len(book.catalogue) % 3 else 3,
        'latest_chapter_id': book.catalogue[-1].chapter_id,
        'latest_chapter_name': book.catalogue[-1].chapter_name,
        'manager': user and user['urole'] == 1
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


@app.route('/logout')
def authority_logout():
    """ 退出登录 """
    user = session.get('user')
    if user: session['user'] = None
    return redirect('/login')


@app.route('/manager')
def authority_manager():
    """ 后台管理界面 """
    user = session.get('user')
    if not user: return redirect('/login')

    service = ServerService()
    codes = service.get_all_authcode()
    render_dict = {
        'res': RES,
        'codes': codes,
        'user': session['user']
    }
    return render_template('authority_manager.html', **render_dict)


@app.route('/updateBookStatus', methods=['POST'])
def update_book_status():
    """ 更改书籍完结状态 """
    user = session.get('user')
    if not user: return redirect('/login')

    service = DBService()
    book_id = request.form.get('book_id')
    finish_status = request.form.get('finish_status')
    data = {'finish_status': int(finish_status)}
    service.update_book_by_id(book_id=int(book_id), data=data)
    return '修改成功'


@app.route('/addAuthcode', methods=['POST'])
def add_authcode():
    """ 添加鉴权码 """
    user = session.get('user')
    if not user: return redirect('/login')

    service = ServerService()
    authcode = request.form.get('authcode')
    valid_times = request.form.get('valid_times')
    if authcode == '$random$':
        valid_times = 50
        authcode = get_random_authcode()
    aid = service.dbService.save_authcode(code=authcode, valid_times=valid_times)
    return json.dumps({'aid': aid, 'authcode': authcode, 'valid_times': valid_times, 'status': 1}, ensure_ascii=False)


@app.route('/removeAuthcode', methods=['POST'])
def remove_authcode():
    """ 删除鉴权码 """
    user = session.get('user')
    if not user: return redirect('/login')

    aid = request.form.get('aid')
    if not aid: return 'Error'
    aid = int(aid)
    service = DBService()
    service.delete_authcode(aid=aid)


@app.route('/updateAuthcode', methods=['POST'])
def update_authcode():
    """ 修改鉴权码 """
    user = session.get('user')
    if not user: return redirect('/login')

    service = DBService()
    aid = request.form.get('aid')
    valid_times = request.form.get('valid_times')
    service.update_authcode(aid=aid, valid_times=valid_times)
    return '修改成功'


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
    url = request.form.get('url')
    item = service.dbService.query_download_item_by_url(url=url)
    if item:
        item.download_state = 0
        service.dbService.update_download_item_by_id(download_item=item)
        return '[]'
    print('转存：', url)
    service.decrease_authority(session[AUTH_KEY], times=5)
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
    app.run(host=host, port=port)
