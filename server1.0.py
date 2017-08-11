# 1.0 你好，web
import http.server

# 原课程里面使用的是BaseHTTPServer模块
# 不过BaseHTTPServer只存在Python2标准库中，在Python3中，你应该使用http.server模块:
class RequestHandler(http.server.BaseHTTPRequestHandler):
    '''处理请求并返回页面'''

    # 页面模板
    Page = '''\
        <html>
        <body>
        <p>Hello, web!</p>
        </body>
        </html>
    '''

    # 处理一个GET请求
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(self.Page)))
        self.end_headers()
        self.Page = bytes(self.Page, encoding="utf-8")
        self.wfile.write(self.Page)  # python3中，写回客户端的输出流要求是二进制格式的

if __name__ == '__main__':
    try:
        serverAddress = ('127.0.0.1', 8080)
        server = http.server.HTTPServer(serverAddress, RequestHandler)
        print('Started http server')
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()