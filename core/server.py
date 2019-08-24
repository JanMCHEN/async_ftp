import asyncio
import json
import re
import time

from .command import CommandParse
from ..conf.settings import *
from ..conf.db import SqliteDB as Sql


async def handle(reader, writer):
    server = Server(reader, writer)
    await server._handle()
    writer.close()


async def main(ip, port):
    if not os.path.exists(USER_DIR):
        os.makedirs(USER_DIR)
    if not os.path.isfile(LOGFILE):
        os.makedirs(os.path.dirname(USER_DIR))
    Sql()
    server = await asyncio.start_server(handle, ip, port)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


def save(file, data):
    with open(file, 'ab') as f:
        f.write(data)


class Server:
    def __init__(self, reader, writer):
        self.times = 0
        self.reader = reader
        self.writer = writer
        self.loop = asyncio.get_running_loop()

    async def _get(self, msg, data):
        path = msg.pop('path')
        size = msg.pop('size')
        self.writer.write(json.dumps(msg).encode())
        await self.writer.drain()
        count = await self.reader.read(32)
        count = json.loads(count.decode().strip()).get('size')
        if count == -1 or size + count > MAXSIZE:
            self.writer.write(b'no')
            await self.writer.drain()
            return

        self.writer.write(b'ok')
        await self.writer.drain()

        file = os.path.join(path, re.split(r'[/\\]', data[1])[-1])
        # print(file)
        if not os.path.isfile(file):
            seek = 0
        else:
            seek = os.path.getsize(file)

        self.writer.write(str(seek).encode())
        await self.writer.drain()

        fd = await self.loop.run_in_executor(None, open, file, 'ab')

        while True:
            if seek < count:
                data = await self.reader.read(1024)
                await self.loop.run_in_executor(None, fd.write, data)
                seek += len(data)
            else:
                break
        fd.close()

        # 存在延迟，客户端发送完，但服务端还没保存完，故最后发送一个完成信号
        self.writer.write('$'.encode())
        await self.writer.drain()

    async def _post(self, msg):
        file = msg.pop('file')
        self.writer.write(json.dumps(msg).encode())
        await self.writer.drain()
        seek = await self.reader.read(32)
        try:
            seek = int(seek)
        except ValueError:
            return

        res = await self.loop.run_in_executor(None, self._send, file, seek)
        for byte in res:
            self.writer.write(byte)
            await self.writer.drain()

    async def _handle(self):
        addr = self.writer.get_extra_info('peername')
        print(f'get new client {addr!r}')
        info = repr(addr) + ' connected at ' + time.asctime(time.localtime(time.time())) + '\n'
        await self.loop.run_in_executor(None, save, LOGFILE, info.encode())

        while True:
            data = await self.reader.read(1024)
            if not data:
                break

            data = json.loads(data.decode())
            if not hasattr(self, data.get('do').strip('_')):
                break

            try:
                ret = await getattr(self, data.get('do').strip('_'))(**data)
                if ret == 'ok':
                    await self.act(data.get('user'), code=CODE)
                    break
                elif ret == 'out':
                    print('stop someone')
                    break
            except TypeError:
                break

    async def auth(self, **kwargs):
        msg = ''
        user = kwargs.get('user')
        res = await self.loop.run_in_executor(None, Sql.find_one, user)
        if res is not None and res[1] == kwargs.get('pwd'):
            msg = 'ok'

        if not msg:
            msg = 'Authentication failure'
            self.times += 1
        if self.times >= RETRY:
            msg = 'out'

        self.writer.write(msg.encode())
        await self.writer.drain()

        return msg

    async def sign_up(self, **kwargs):
        try:
            kwargs.pop('do')
        except KeyError:
            return
        user = kwargs.get('user', '')
        pwd = kwargs.get('pwd', '')

        if len(pwd) < 2 or len(user) < 2 or len(user) > 15:
            msg = 'Please confirm that the length of ID you entered matches the standard(at least 2,at most 15)'
        else:
            res = await self.loop.run_in_executor(None, Sql.find_one, user)
            if res is not None:
                msg = 'The user already exists'
            else:
                await self.loop.run_in_executor(None, Sql.insert_one, user, pwd)
                msg = 'ok'
        self.writer.write(msg.encode())
        await self.writer.drain()
        return msg

    async def act(self, user, mode=0, code=None):
        if code != CODE:
            print(f'{user!r}非法访问')
            return
        path = USER_DIR + '/' + user
        if not os.path.exists(path):
            os.makedirs(path)
            os.makedirs(os.path.join(path, '.temp'))
        cp = CommandParse(path, self.writer, self.reader)
        while True:
            data = await self.reader.read(1024)
            if not data:
                break
            msg = {}
            data = data.decode().split()
            if hasattr(CommandParse, data[0].strip('_')):
                msg = await self.loop.run_in_executor(None, getattr(CommandParse, data[0].strip('_')), cp, data)
            else:
                msg['note'] = "{} not the inside command".format(data[0])

            if msg is None:
                continue
            if msg.get('loop') == 'post':
                await self._get(msg, data)
                continue
            if msg.get('loop') == 'get':
                await self._post(msg)
                continue

            self.writer.write(json.dumps(msg).encode())
            await self.writer.drain()

            if msg.get('exit'):
                print(f'{user} out')
                break

    def _send(self, file, seek):
        with open(file, 'rb') as f:
            f.seek(seek)
            yield from f.readlines()
