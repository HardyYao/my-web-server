# 显示请求信息
import http.server

class RequestHandler(http.server.BaseHTTPRequestHandler):
    """处理请求并返回页面"""

    # 页面模板
    Page = '''\
        <html>
        <body>
        <table>
        <tr>  <td>Header</td>         <td>Value</td>          </tr>
        <tr>  <td>Date and time</td>  <td>{date_time}</td>    </tr>
        <tr>  <td>Client host</td>    <td>{client_host}</td>  </tr>
        <tr>  <td>Client port</td>    <td>{client_port}</td> </tr>
        <tr>  <td>Command</td>        <td>{command}</td>      </tr>
        <tr>  <td>Path</td>           <td>{path}</td>         </tr>
        </table>
        </body>
        </html>
    '''

    # 处理一个GET请求
    def do_GET(self):
        page = self.create_page()
        self.send_content(page)

    # 实现create_page
    def create_page(self):
        values = {
            'date_time': self.date_time_string(),
            'client_host': self.client_address[0],
            'client_port': self.client_address[1],
            'command': self.command,
            'path': self.path
        }
        page = self.Page.format(**values)
        return page

    # send_content 与之前 do_GET 内的代码几乎一样：
    def send_content(self, page):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        page = bytes(page, encoding="utf-8")
        self.wfile.write(page)


if __name__ == '__main__':
    try:
        serverAddress = ('127.0.0.1', 8080)
        server = http.server.HTTPServer(serverAddress, RequestHandler)
        print("Started http server")
        server.serve_forever()
    except KeyboardInterrupt:
        print("^C received, shuting down the server")
        server.socket.close()