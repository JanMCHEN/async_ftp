import os

IP = "127.0.0.1"
PORT = 8888
RETRY = 5
CODE = 'dreaming'
MAXSIZE = 100000000
# ACCOUNTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'accounts.json')
LOGFILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logger', 'logs.log')
USER_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'User')
DATA_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'conf', 'user.db')

