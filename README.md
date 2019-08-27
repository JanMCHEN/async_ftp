# async_ftp
异步版socket服务器

## 基于asyncio的事件循环支持多用户同时访问
Tcp socket建立连接，每一个客户端接入加入事件循环，每等待一次网络I/O事件将控制权交给主循环，实现类似轮询操作。
对于访问本地文件系统以及数据库查询的阻塞操作，采用Executor线程池防止阻塞主事件循环线程。

## 启动(python 3.7)
在项目所在目录运行
`python -m  async_ftp.bin.run`
## 参数
    -H,--host  	指定ip地址，	默认127.0.0.1
    —P,--port  	指定端口，	默认8888
    -h,--help:		查看帮助信息
    默认配置可在conf.settings里边修改
## 客户端
在client目录，可以单独使用，启动：
`python client.py`,更多配置请查看client目录下了readme.txt
客户端也修改为异步版本，但其实目前还没有提供其它操作，上传和下载时默认阻塞
## 简介
根据之前多线程版重构，加入sqlite数据库保存以及验证用户信息，用户空间限额，显示字体优化，去除聊天室支持，后续有时间编写python版
```shell
ls:[path]	     	#查看当前目录所有文件
cd：[path]		     #切换目录
rm: path or file		#删除目录或文件
mkdir:path				#新建目录
detail:path or file     # 获取大小
send:file [path]		#上传本地文件至path
get:file [path]	#下载文件至本地path
sendto:file user		#发送文件至用户，默认发送至用户目录的./temp目录下
```
