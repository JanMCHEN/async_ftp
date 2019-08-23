import sqlite3

from .settings import DATA_BASE


class SqliteDB:
    def __init__(self):
        coon = sqlite3.connect(DATA_BASE)
        c = coon.cursor()
        # Create table
        c.execute('''CREATE TABLE if not exists user
                     (username text, password text, mode real, size real)''')
        coon.commit()
        coon.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @staticmethod
    def insert_one(username, password):
        coon = sqlite3.connect(DATA_BASE)
        c = coon.cursor()
        c.execute("INSERT INTO user VALUES (?,?,0, 0)", (username, password))
        coon.commit()
        coon.close()

    @staticmethod
    def find_one(username):
        coon = sqlite3.connect(DATA_BASE)
        c = coon.cursor()
        c.execute("select * from user where username=?", (username,))
        res = c.fetchone()
        coon.close()
        return res

    @staticmethod
    def update_one(username, size):
        coon = sqlite3.connect(DATA_BASE)
        c = coon.cursor()
        c.execute('UPDATE user SET size=? WHERE username=?', (size, username))
        coon.commit()
        coon.close()


if __name__ == '__main__':
    SqliteDB().update_one('aaaaa', 0)
