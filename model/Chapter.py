class Chapter(object):
    """
    self.url: 章节链接
    self.content: 章节内容
    self.display_name: 带章节数的名称

    self.chapter_index: 章节数
    self.chapter_name: 不带章节数的名称
    """
    def __init__(self, display_name: str, content: str, url: str, chapter_id=-1, order_id=-1, book_id=-1):
        self.url = url
        self.content = content
        self.order_id = order_id
        self.chapter_id = chapter_id
        self.book_id = book_id
        self.display_name = display_name.strip()

    def __str__(self):
        return f"{self.chapter_id}\t{self.order_id}\t{self.display_name}\t{self.url}\n{self.content}"

    def get_db_dict(self):
        return {
            'content': self.content,
            'order_id': self.order_id,
            'display_name': self.display_name
        }
