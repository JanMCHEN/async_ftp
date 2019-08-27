import asyncio
import optparse
import json
import os


def info_pack(do, **kwargs):
    # 将要发送的消息打包，便于发送及服务端识别
    kwargs['do'] = do
    return json.dumps(kwargs).encode('utf-8')


def progress_bar(have, total):
    """
    进度条，
    :param have: 已经传送的
    :param total: 总共需要传送的
    :return:
    """
    done = have/total*100
    info = '\033[1;44m|' + '#' * int(done/2) + '\033[0m'
    print('\r' + '\033[1;32m{:.2f}\033[0m%'.format(done) + info, end='')


def help_info(file=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'readme.txt')):
    with open(file, 'r') as f:
        info = f.readlines()
    for inf in info:
        print('\033[1;44m', inf.strip(), '\033[0m')


def file_read(file, seek):
    with open(file, 'rb') as f:
        f.seek(seek)
        for chunk in f:
            yield chunk


class ClientSocket:
    def __init__(self, file_dir=None):
        self.writer = self.reader = None
        self.file_dir = file_dir
        if file_dir is None:
            self.file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'file')
        if not os.path.isdir(self.file_dir):
            os.mkdir(self.file_dir)
        op = optparse.OptionParser()
        op.add_option("-I", "--ip", dest="ip")
        op.add_option("-P", "--port", dest="port")
        op.add_option("-u", "--username", dest="username")
        op.add_option("-p", "--password", dest="password")
        options, args = op.parse_args()
        # 程序入口
        asyncio.run(self.verify_args(options, args))

    async def verify_args(self, opt, args):
        """
        对程序启动时传入的参数作解析
        :param opt:
        :param args:
        :return:
        """
        if args and args[0] == 'help':
            help_info()
            return
        if not opt.ip:
            opt.ip = "127.0.0.1"
        if not opt.port:
            opt.port = 8888
        self.reader, self.writer = await asyncio.open_connection(opt.ip, opt.port)
        if not opt.username:
            ch = input("SignIn or SignUp[I/U]:")
            if ch.upper() == 'I':
                opt.username = input("Your name:")
                opt.password = input("Password:")
            elif ch.upper() == "U":
                while True:
                    res = await self.sign_up()
                    if not res:
                        break
                return
            else:
                print("\033[1;31m sorry!\033[0m")
                return
        elif not opt.password:
            opt.password = input("Password:")
        await self.sign_in(opt.username, opt.password)

    async def sign_up(self):
        """注册"""
        user = input("input a username:")
        pw = input("put your code:")
        if pw == input("make sure your code:"):
            self.writer.write(info_pack('sign_up', user=user, pwd=pw))
            await self.writer.drain()
            data = await self.reader.read(128)
            if data.strip() == b'ok':
                await self.act(user)
                return
            else:
                print(data)
                if input("Again?[Y/N]").upper() == 'Y':
                    return True
        else:
            if input("two different code,again?[Y/N]").upper() == 'Y':
                return True

    async def sign_in(self, user, pw):
        """登录"""
        self.writer.write(info_pack('auth', user=user, pwd=pw))
        await self.writer.drain()

        data = await self.reader.read(128)
        if data.strip() == b'ok':
            await self.act(user)
        elif data.strip() == b'out':
            return
        else:
            print(data)
            await self.sign_in(input("Your name:"), input("Password:"))

    async def get(self, file, seek, size):
        seek = int(seek)
        with open(file, 'ab') as f:
            f.seek(seek, 0)
            while True:
                if seek < size:
                    data = await self.reader.read(1024)
                    f.write(data)
                    seek += len(data)
                    progress_bar(seek, size)
                else:
                    print('\n\033[1;34m finished \033[0m')
                    break

    async def send(self, file, seek, size):
        seek = int(seek)
        res = file_read(file, seek)
        for data in res:
            self.writer.write(data)
            await self.writer.drain()
            seek += len(data)
            progress_bar(seek, size)
        # 等待一个完成信号
        await self.reader.read(1)
        print('\n\033[1;34m finished \033[0m')

    async def act(self, user):
        """用户进入后所有的操作在这里识别发送给服务器并执行相应的操作"""
        dirs = user
        print("Welcome to ftp server...{}".format(user))
        while True:
            cmd = input('\r:' + dirs + '>')
            if cmd == 'help':
                help_info()
                continue
            if len(cmd) == 0:
                continue

            self.writer.write(cmd.encode("utf8"))
            await self.writer.drain()

            response = await self.reader.read(1024)
            if len(response) == 0:
                continue
            try:
                res = json.loads(response.decode().strip())
            except json.decoder.JSONDecodeError:
                print('错误的回应')
                continue
            if res.get('exit'):
                break
            if res.get('dir'):
                dirs = res['dir']
            if res.get('note'):
                print('\033[1;32m', res['note'], '\033[0m', sep='')
            if res.get('loop') == 'post':
                file = cmd.split()[1]
                file = os.path.abspath(file)
                msg = {}
                if os.path.isfile(file):
                    msg['size'] = os.stat(file).st_size
                else:
                    msg['size'] = -1

                self.writer.write(json.dumps(msg).encode())
                await self.writer.drain()

                rec = await self.reader.read(2)
                ok = rec.strip() == b'ok'
                if not ok:
                    print('\033[1;31m Space full or File not Exist \033[0m')
                    continue
                seek = await self.reader.read(32)
                await self.send(file, seek, msg['size'])
                continue

            if res.get('loop') == 'get':
                cmd = cmd.split()
                size = res.get('size')
                seek = 0
                file = res.get('file_name')
                path = self.file_dir
                if len(cmd) == 3:
                    path, file = os.path.split(cmd[-1])
                    if not os.path.exists(path):
                        path = self.file_dir
                        print(f'\033[1;33m{path} not found,save at default dir \033[0m')

                    if not file:
                        file = res.get('file_name')
                file = os.path.join(path, file)

                if os.path.isfile(file):
                    seek = os.stat(file).st_size
                if seek:
                    if not input("continue with any inputs:"):
                        print('Reload..')
                        seek = 0
                self.writer.write(str(seek).encode())
                await self.writer.drain()
                await self.get(file, seek, size)


if __name__ == "__main__":
    try:
        cs = ClientSocket()
    except (KeyboardInterrupt, ConnectionResetError):
        pass

