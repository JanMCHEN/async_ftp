支持cd、mkdir、rm、ls，upload、download等操作，exit退出
参数说明：
[-i][--ip]:指定要连接的ip,默认localhost
[-P][--port]:指定端口号，默认8888
[-u][--user]:用户名
[-p][--password]:密码
操作说明：
cd [path]:切换当前目录，cd不带参数可返回当前目录
ls [path]:返回所要查询目录下的文件及子目录
detail [file or path]:获取大小
upload file [path]:上传文件
download file [path]:下载文件至本地
sendto file user: 发送文件给指定用户
exit:退出