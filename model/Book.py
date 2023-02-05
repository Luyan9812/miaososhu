from os.path import join, exists


class Book(object):
    """
    self.url: 书籍首页链接
    self.info: 内容简介
    self.book_name: 书籍名称
    self.book_type: 书籍类别
    self.author_name: 作者名称
    self.update_time: 最后更新时间
    self.cover_img: 书籍封面链接
    self.finish_status: 状态完结【-1：未知，0：未完结，1：已完结】

    self.catalogue: 书籍目录
    self.chapter_list: 章节列表
    self.total_chapter: 总章节数
    self.current_chapter: 已爬取章节数
    """

    def __init__(self, book_name: str, author_name: str, update_time: str,
                 book_type: str, info: str, finish_status: int, url: str, cover_img: str, book_id=-1):
        self.book_id = book_id
        self.url = url.strip()
        self.info = info.strip()
        self.book_name = book_name.strip()
        self.book_type = book_type.strip()
        if not self.book_type: self.book_type = '未知'
        self.author_name = author_name.strip()
        self.update_time = update_time.strip()
        self.cover_img = cover_img
        self.finish_status = finish_status

        # 目录的键值对是"章节名：章节链接"
        self.catalogue = []
        self.chapter_list = []
        self.total_chapter = 0
        self.current_chapter = 0

        fname = f'{self.book_name}_{self.author_name}'
        self.save_txt_path = join('/Users/luyan/Desktop/小说/txt', fname + '.txt')
        self.save_img_path = join('/Users/luyan/Desktop/小说/封面图', fname + '.jpg')
        self.save_epub_path = join('/Users/luyan/Desktop/小说/epub', fname + '.epub')

        self.finish_describe = {-1: '未知', 0: '连载中', 1: '完结'}

    def get_latest_chapter_name(self):
        """ 获取最新章节的名称 """
        return self.catalogue[-1].chapter_name if len(self.catalogue) > 0 else ''

    def get_finish_status_info(self):
        return self.finish_describe.get(self.finish_status, '未知')

    def get_db_dict(self):
        return {'book_name': self.book_name, 'author_name': self.author_name,
                'finish_status': self.finish_status, 'update_time': self.update_time,
                'url': self.url, 'cover_img': self.cover_img, 'info': self.info}

    def save(self, content, need_save_txt=True):
        """ 将书籍保存 """
        # 保存封面图
        if content is not None:
            with open(self.save_img_path, 'wb') as f:
                f.write(content)
        if need_save_txt:
            self.save_txt()

    def save_txt(self):
        """ 将小说保存成 txt 格式 """
        with open(self.save_txt_path, 'w') as f:
            f.write("书籍描述信息\n\n" + self.desc())
            for chapter in self.chapter_list:
                f.write('\n\n\n' + chapter.display_name + '\n\n')
                f.write(chapter.content)

    def desc(self):
        """ 获取书籍的描述信息 """
        desc = f'书名：《{self.book_name}》\n'
        desc += f'作者：{self.author_name}\n'
        desc += f'类别：{self.book_type}\n'
        desc += f'章节数：{self.current_chapter}/{self.total_chapter}\n'
        desc += f'状态：{self.get_finish_status_info()}\n'
        desc += f'最后更新时间：{self.update_time}\n'
        desc += f'首页网址：{self.url}\n'
        desc += f'封面网址：{self.cover_img}\n'
        desc += f'简介：{self.info}\n\n\n'
        return desc

    def __str__(self):
        return f"{self.book_name}\t{self.author_name}\t{self.update_time}\t" \
               f"{self.book_type}\t{self.info}\t{self.url}\t{self.cover_img}\n" \
               f"{self.current_chapter} / {self.total_chapter}\n{self.catalogue}"
