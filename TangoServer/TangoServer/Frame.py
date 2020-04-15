import os
import time
import pyodbc
from TangoServer import config


class User(object):

    # connect to database
    cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER=localhost;DATABASE=TangoUsers;'
                          'UID=' + config.database_username +
                          ';PWD=' + config.database_password)
    cursor = cnxn.cursor()

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def can_log_in(self):
        """
        can_log_in() -> bool

        If this user's information is right, it will return True, else return False.
        """
        User.cursor.execute(
            'Select * From Users Where username = \'{}\' and password = \'{}\''.format(self.username, self.password))
        row = User.cursor.fetchone()
        if row:
            return True
        else:
            return False

    def register(self):
        """
        register() -> True

        If username is already registered, return False,
        else return True and store the user information in database.
        """
        User.cursor.execute('Select * From Users Where username = \'{}\''.format(self.username))
        row = User.cursor.fetchone()
        if not row:
            User.cursor.execute('Insert into Users Values (\'{}\', \'{}\')'.format(self.username, self.password))
            User.cursor.commit()
            return True
        else:
            return False


class Message(object):
    """
    Store message of message broad.
    """

    def __init__(self, content, sender):
        self.send_time = time.asctime(time.localtime(time.time()))
        self.content = content
        self.sender = sender

    def __str__(self):
        return 'Message from {}:\r\n\t{}\r\n\t\t{}\r\n'.format(self.sender, self.content, self.send_time)


def show_word_pool_list():
    """
    show_word_pool_list() -> str

    Return name of all word_pool the server has.
    """
    return os.listdir('../Resource/word_pool')


if __name__ == '__main__':
    print(show_word_pool_list())
