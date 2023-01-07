import shutil

from os import walk, chdir, makedirs
from os.path import join, split, exists

from zipfile import ZipFile

from model.Book import Book
from model.Chapter import Chapter


def _get_mimetype():
    """ mimetype """
    return 'application/epub+zip'


def _get_container():
    """ META-INF/container.xml """
    return """<?xml version="1.0" encoding="UTF-8" ?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles> 
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""


def _get_content(book: Book):
    """ OEBPS/content.opf """
    content_info = '''<?xml version="1.0" encoding="UTF-8" ?>
<package version="2.0" unique-identifier="PrimaryID" xmlns="http://www.idpf.org/2007/opf">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:language>zh-CN</dc:language>
    <dc:title>{book_name}</dc:title>
    <dc:creator>{author_name}</dc:creator>
    <dc:description>{info}</dc:description>
    <meta name="cover" content="cover-image" />
</metadata>
<manifest>
{manifest}
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="cover-image" href="cover.jpg" media-type="image/jpeg"/>
</manifest>
<spine toc="ncx">
{spine}
</spine>
</package>'''
    spine = ''
    manifest = ''
    for i, chapter in enumerate(book.chapter_list, start=1):
        spine += f'\t<itemref idref="chapter_{i}.html"/>\n'
        manifest += f'\t<item id="chapter_{i}.html" href="chapter_{i}.html" media-type="application/xhtml+xml"/>\n'
    f_map = {"book_name": book.book_name, "author_name": book.author_name,
             "info": book.info, "manifest": manifest, "spine": spine}
    return content_info.format_map(f_map)


def _get_ncx(book: Book):
    """ OEBPS/toc.ncx """
    ncx_info = """<?xml version='1.0' encoding='utf-8'?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
    <head>
        <meta name="dtb:uid" content=" "/>
        <meta name="dtb:depth" content="-1"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle> <text>{book_name}</text> </docTitle>
    <docAuthor> <text>{author_name}</text> </docAuthor>
    <navMap>
{nav_points}
    </navMap>
</ncx>"""
    nav_points = ''
    for i, chapter in enumerate(book.chapter_list, start=1):
        nav_points += f"""
        <navPoint id="chapter_{i}.html" playOrder="{i}">
            <navLabel> <text>{chapter.display_name}</text> </navLabel>
            <content src="chapter_{i}.html"/>
        </navPoint>
        """
    ncx_map = {"book_name": book.book_name, "author_name": book.author_name, "nav_points": nav_points}
    return ncx_info.format_map(ncx_map)


def _get_chapter(chapter: Chapter):
    """ 获取章节html """
    html = """<!DOCTYPE html>
<html>
    <head>
        <title>{display_name}</title>
    </head>
    <body>
        <h3>{display_name}</h3>
        <p>{content}</p>
    </body>
</html>
    """
    content = chapter.content.replace('\n', '<br/>')
    return html.format_map({'display_name': chapter.display_name, 'content': content})


def _create_file(dirpath, filename, content_str):
    """ 创建文件 """
    exists(dirpath) or makedirs(dirpath)
    filepath = join(dirpath, filename.replace('/', '.'))
    with open(filepath, 'w') as f:
        f.write(content_str)


def save_epub(book: Book):
    """ 创建 epub 格式的电子书 """
    store_path = split(book.save_epub_path)[0]
    store_path = join(store_path, book.book_name + '_tmp')
    exists(store_path) or makedirs(store_path)

    # 配置文件创建
    _create_file(store_path, 'mimetype', _get_mimetype())
    _create_file(join(store_path, 'META-INF'), 'container.xml', _get_container())
    _create_file(join(store_path, 'OEBPS'), 'content.opf', _get_content(book))
    _create_file(join(store_path, 'OEBPS'), 'toc.ncx', _get_ncx(book))

    # 封面图复制
    image_to_path = join(store_path, 'OEBPS')
    exists(image_to_path) or makedirs(image_to_path)
    if exists(book.save_img_path):
        shutil.copyfile(book.save_img_path, join(image_to_path, 'cover.jpg'))

    # chapter 文件创建
    for i, chapter in enumerate(book.chapter_list, start=1):
        _create_file(join(store_path, 'OEBPS'), f'chapter_{i}.html', _get_chapter(chapter))

    epub_file = ZipFile(book.save_epub_path, 'w')
    chdir(store_path)
    for root, _, files in walk('.'):
        for f in files:
            epub_file.write(join(root, f))
    epub_file.close()
    shutil.rmtree(store_path)


def main():
    s = '{name}, {name}'.format_map({'name': 'jaxl'})
    print(s)


if __name__ == '__main__':
    main()
