import BaseHTTPServer
import SocketServer
from netconfig import NetworkConfigurator
from get import getJSON
from urlParser import get_parser

init_file = 'initial_network.json'
cur_file = 'current_network.json'
netConfigurator = None


class MyRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()

    def do_GET(self):
        getData = getJSON(netConfigurator.net)
        data = get_parser(self.path, getData)
        self._set_headers()
        self.wfile.write(data);
        pass

    def do_POST(self):
        pass

    def do_PUT(self):
        pass

    def do_DELETE(self):
        pass


def init_net():
    global netConfigurator
    netConfigurator = NetworkConfigurator(initfile=init_file, curfile=cur_file)
    getJSON(netConfigurator.net)


def run_api_server(handler=MyRequestHandler, addr="", port=8000):
    server_address = (addr, port)
    httpd = SocketServer.TCPServer(server_address, handler)

    print("Starting httpd server on %s:%s" % (addr, port))
    httpd.serve_forever()


if __name__ == "__main__":
    init_net()
    run_api_server()
