class DownloadItem(object):
    """ 转存列表 """
    def __init__(self, url, download_state, qid=-1):
        self.url = url
        self.qid = qid
        self.download_state = download_state

    def __str__(self):
        return f'{self.qid}, {self.url}, {self.download_state}'
