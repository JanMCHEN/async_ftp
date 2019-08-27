import os
import shutil


def get_size(path, size=0):
    file_list = os.listdir(path)
    for file in file_list:
        file = os.path.join(path, file)
        if os.path.isfile(file):
            size += os.stat(file).st_size
        elif os.path.isdir(file):
            size += get_size(file, size)
    return size


class CommandParse(object):

    def __init__(self, path, writer, reader):
        self.home = os.path.abspath(path)
        self.path = self.home
        self.writer = writer
        self.reader = reader
        self.file_size = get_size(self.home)

    def _path_parser(self, path, types=0):
        msg = {}
        if isinstance(path, str):
            path = path.split('/')
            dirs = self.path
            for p in path:
                if p == '.' * len(p):
                    for _ in range(len(p) - 1):
                        if self.home == dirs:
                            break
                        dirs = os.path.dirname(os.path.abspath(dirs))
                else:
                    # print(dirs)
                    dirs = os.path.join(dirs, p)
            if not os.path.exists(dirs):
                if types == 1:
                    msg['note'] = 'Not found the directory'
                elif types == 2:
                    os.makedirs(dirs)
                    msg['note'] = 'done'
                elif types == 3:
                    msg['note'] = "Can't open the directory"
            else:
                if types == 1:
                    self.path = dirs
                elif types == 2:
                    msg['note'] = 'The directory exist'
                elif types == 3:
                    msg['note'] = '\n'.join(os.listdir(dirs))
                elif not types:
                    msg['dirs'] = dirs
        else:
            msg['note'] = 'path_parser is not inside command'
        return msg

    def cd(self, data):
        msg = {}
        if len(data) == 1:
            msg['note'] = os.path.relpath(self.path, os.path.dirname(self.home))
        elif len(data) == 2:
            if data[1] == '.':
                self.path = self.home
            elif data[1] == '.' * len(data[1]):
                for _ in range(len(data[1])-1):
                    if self.home == self.path:
                        break
                    self.path = os.path.dirname(os.path.abspath(self.path))
            else:
                msg = self._path_parser(data[1], 1)
        else:
            return {'note': 'cd [path]'}
        msg['dir'] = os.path.relpath(self.path, os.path.dirname(self.home))
        return msg

    def mkdir(self, data):
        if len(data) == 2:
            return self._path_parser(data[1], 2)
        else:
            return {'note': 'mkdir [path]'}

    def ls(self, data):
        msg = {}
        if len(data) == 1:
            msg['note'] = '\n'.join(os.listdir(self.path))
            return msg
        elif len(data) == 2:
            return self._path_parser(data[1], 3)

    def rm(self, data):
        msg = {}
        if len(data) == 2:
            path = os.path.split(data[1])[0]
            if path:
                path = self._path_parser(path).get('dirs')
            else:
                path = self.path
            if path:
                file = os.path.split(data[1])[-1]
                if file:
                    file = os.path.join(path, file)
                    if os.path.isfile(file):
                        self.file_size -= os.stat(file).st_size
                        os.remove(file)
                        msg['note'] = 'done'
                    else:
                        msg['note'] = 'file not found'
                else:
                    self.file_size -= get_size(path)
                    os.rmdir(path)
                    msg['note'] = 'done'
            else:
                msg['note'] = 'path not exist'
        else:
            msg['note'] = 'rm [file]'
        return msg

    def detail(self, data):
        if len(data) == 2:
            file = os.path.join(self.path, data[1])
            if os.path.isfile(file):
                size = os.stat(file).st_size
            elif os.path.isdir(file):
                size = get_size(file)
            else:
                size = 'file not found'
            msg = {'note': str(size)}
        else:
            msg = {'note': 'detail [path]or[file]'}
        return msg

    def send(self, data):
        self.file_size = get_size(self.home)
        dirs = ''
        if len(data) == 1:
            return {'note': 'send [file] [path]'}
        elif len(data) == 2:
            dirs = self.path
        elif len(data) == 3:
            msg = self._path_parser(data[2])
            dirs = msg.get('dirs')
        if not dirs:
            return {'note': 'Path not exist '}

        return {'loop': 'post', 'path': dirs, 'size': self.file_size}

    def get(self, data):
        if len(data) == 3 or len(data) == 2:
            path = os.path.split(data[1])[0]
            if path:
                msg = self._path_parser(path)
                dirs = msg.get('dirs')
            else:
                dirs = self.path
        else:
            return {'note': 'get [file] [path]'}

        if not dirs:
            return {'note': 'path not found '}

        file = os.path.join(dirs, os.path.split(data[1])[-1])
        if not os.path.isfile(file):
            return {'note': 'file not exist '}

        size = os.path.getsize(file)
        msg = {
            'loop': 'get',
            'file_name': os.path.split(data[1])[-1],
            'size': size,
            'file': file,
        }
        return msg

    def sendto(self, data):
        if len(data) == 3:
            target = os.path.join(os.path.dirname(os.path.abspath(self.home)), data[2])
            if os.path.isdir(target):
                path = os.path.split(data[1])[0]
                if path:
                    msg = self._path_parser(path)
                    dirs = msg.get('dirs')
                else:
                    dirs = self.path
                if not dirs:
                    return {'note': 'path not found '}

                file = os.path.join(dirs, os.path.split(data[1])[-1])
                if not os.path.isfile(file):
                    return {'note': 'file not exist '}

                if file:
                    shutil.copy(file, os.path.join(target, '.temp', os.path.split(file)[-1]))
                    return {'note': 'done'}
            else:
                return {'note': 'user not exits'}
        else:
            return {'note': 'sendto [file] [user]'}

    def exit(self, data):
        return {'exit': True}

