# CGI协议
import os, http.server
import subprocess

class ServerException(Exception):
    """服务器内部错误"""
    pass

class base_case(object):
    """条件处理基类"""
    def handle_file(self, handler, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            handler.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(full_path, msg)
            handler.handle_error(msg)

    def index_path(self, handler):
        return os.path.join(handler.full_path, "index.html")

    # 要求子类必须实现该接口
    def test(self, handler):
        assert False, 'Not implemented.'

    def act(self, handler):
        assert False, 'Not implemented.'

# 子类继承基类，依此类推
class case_directory_index_file(base_case):
    """在该路径下返回首页"""

    # 判断目标路径是否是目录&&目录下是否有index.html
    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
                os.path.isfile(self.index_path(handler))

    # 响应index.html的内容
    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))

class case_no_file(base_case):
    """文件或目录不存在"""

    def test(self, handler):
        return not os.path.exists(handler.full_path)


    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))


class case_existing_file(base_case):
    """文件存在的情况"""

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)


class case_cgi_file(base_case):
    """脚本文件处理"""

    def test(self, handler):
        return os.path.isfile(handler.full_path) and \
               handler.full_path.endswith('.py')

    def act(self, handler):
        self.run_cgi(handler)

    def run_cgi(self, handler):
        data = subprocess.check_output(["python", handler.full_path])
        handler.send_content(data)

class case_always_fail(base_case):
    """所有情况都不符合时的默认处理类"""

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))

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
        self.wfile.write(content)

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        content = bytes(content, encoding="utf-8")
        self.send_content(content, 404)

if __name__ == '__main__':
    try:
        serverAddress = ('127.0.0.1', 8080)
        server = http.server.HTTPServer(serverAddress, RequestHandler)
        print("Started http server")
        server.serve_forever()
    except KeyboardInterrupt:
        print("^C received, shuting down the server")
        server.socket.close()