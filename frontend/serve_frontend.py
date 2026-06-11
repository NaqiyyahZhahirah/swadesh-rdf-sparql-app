import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8000
HERE = Path(__file__).resolve().parent

class SilentHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    handler = lambda *args, **kwargs: SilentHTTPRequestHandler(*args, directory=str(HERE), **kwargs)
    with socketserver.TCPServer(('127.0.0.1', PORT), handler) as httpd:
        url = f'http://127.0.0.1:{PORT}/index.html'
        print('Serving frontend at', url)
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nServer stopped.')
