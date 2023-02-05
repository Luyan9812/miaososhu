class Catalogue(object):
    """ 目录类 """
    def __init__(self, chapter_name, chapter_url, catalogue_id=-1, book_id=-1, chapter_id=-1):
        self.chapter_name = chapter_name
        self.chapter_url = chapter_url
        self.catalogue_id = catalogue_id
        self.book_id = book_id
        self.chapter_id = chapter_id

