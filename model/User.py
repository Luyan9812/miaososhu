class User(object):
    """ 用户类 """
    def __init__(self, uname, upassword, urole=0, umail='', uid=-1):
        self.uid = uid
        self.umail = umail
        self.urole = urole
        self.uname = uname
        self.upassword = upassword

    def get_dict(self):
        return {
            'uid': self.uid,
            'uname': self.uname,
            'upassword': self.upassword,
            'urole': self.urole,
            'umail': self.umail
        }

    def __str__(self):
        return f'{self.uid}, {self.uname}, {self.upassword}, {self.urole}, {self.umail}'
