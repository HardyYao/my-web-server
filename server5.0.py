# CGI协议
import os, http.server
import subprocess

class ServerException(Exception):
    """服务器内部错误"""
    pass

class case_no_file(object):
    """路径不存在"""

    def test(self, handler):
        return not os.path.exists(handler.full_path)


    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))


class case_existing_file(object):
    """该路径是文件"""

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        handler.handle_file(handler.full_path)


class case_always_fail(object):
    """所有情况都不符合时的默认处理类"""

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))

class case_directory_index_file(object):
    """在 http://127.0.0.1:8080/ 显示首页"""

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    # 判断目标路径是否是目录&&目录下是否有index.html
    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
                os.path.isfile(self.index_path(handler))

    # 响应index.html的内容
    def act(self, handler):
        handler.handle_file(self.index_path(handler))

class case_cgi_file(object):
    """脚本文件处理"""

    def test(self, handler):
        return os.path.isfile(handler.full_path) and \
                handler.full_path.endswith('.py')

    def act(self, handler):
        # 运行脚本文件
        handler.run_cgi(handler.full_path)

class RequestHandler(http.server.BaseHTTPRequestHandler):
    '''
    请求路径合法则返回相应处理
    否则返回错误页面
    '''

    # 错误页面模板
    Error_Page = '''\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        '''

    # 所有可能的情况
    Cases = [case_no_file(),
             case_cgi_file(),
             case_existing_file(),
             case_directory_index_file(),
             case_always_fail()]

    def do_GET(self):
        try:
            # 文件完整路径
            self.full_path = os.getcwd() + self.path

            # 遍历所有可能的情况
            for case in self.Cases:
                # 如果满足该情况
                if case.test(self):
                    # 调用相应的act函数
                    case.act(self)
                    break

        # 处理异常
        except Exception as msg:
            self.handle_error(msg)

    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        # content = bytes(content, encoding="utf-8")    # 处理脚本文件时添加这行代码会出错
        self.wfile.write(content)

    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as reader:   # 将打开文件方式更改为'rb'，以字节格式读取
                content = reader.read()
            self.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            self.handle_error(msg)

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        content = bytes(content, encoding="utf-8")  # 将错误信息转换为字节格式
        self.send_content(content, 404)

    def run_cgi(self, full_path):
        data = subprocess.check_output(["python", full_path])
        self.send_content(data)

if __name__ == '__main__':
    try:
        serverAddress = ('127.0.0.1', 8080)
        server = http.server.HTTPServer(serverAddress, RequestHandler)
        print("Started http server")
        server.serve_forever()
    except KeyboardInterrupt:
        print("^C received, shuting down the server")
        server.socket.close()