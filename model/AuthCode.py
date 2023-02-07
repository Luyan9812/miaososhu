class AuthCode(object):
    """ 鉴权码对象 """
    def __init__(self, authcode, valid_times, aid=-1):
        self.aid = aid
        self.authcode = authcode
        self.valid_times = valid_times
