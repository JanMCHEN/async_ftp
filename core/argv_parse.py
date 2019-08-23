import asyncio
import optparse


from ..conf.settings import *
from ..core.server import main


class ArgvParse:
    """控制台命令解析"""
    def __init__(self):
        op = optparse.OptionParser()
        op.add_option("-I", "--ip", dest="ip")
        op.add_option("-P", "--port", dest="port")
        self.options, self.args = op.parse_args()
        self._verify_args()

    def _verify_args(self):
        if not self.options.ip:
            self.options.ip = IP
        if not self.options.port:
            self.options.port = PORT
        if self.args:
            fun = self.args[0].strip('_')
            if hasattr(self, fun):
                getattr(self, fun)()
            else:
                print('invalid param')
                self.help()

    def start(self):
        try:
            asyncio.run(main(self.options.ip, self.options.port))
        except KeyboardInterrupt:
            return

    def help(self):
        info = ['[-i][--ip]:指定绑定的ip，默认绑定localhost', '[-P][--port]:指定端口号，默认8888',
                '配置参数>>:', 'start:启动', 'help:帮助信息', 'more:更多信息']
        for inf in info:
            print(inf)

    def more(self):
        print('敬请期待')
