import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs


HOST = 'localhost'
PORT = 8000


def read_file(path: str) -> bytes:
    """Читает файл через контекстный менеджер и возвращает байты."""
    with open(path, 'rb') as f:
        return f.read()


class MyHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP-запросов."""

    def _send_html(self, filename: str, status: int = 200) -> None:
        """Отправляет HTML-файл клиенту."""
        try:
            body = read_file(filename)
        except FileNotFoundError:
            # файл отсутствует — отдаём 404
            self._send_html('404.html', status=404)
            return

        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        """На ЛЮБОЙ GET-запрос отдаём страницу контактов."""
        try:
            self._send_html('contacts.html', status=200)
        except Exception:
            self._send_html('500.html', status=500)

    def do_POST(self) -> None:
        """Принимает POST, печатает данные в консоль."""
        try:
            length = int(self.headers.get('Content-Length', 0))
            raw = self.rfile.read(length).decode('utf-8')
            data = parse_qs(raw)

            print('\n=== POST-запрос ===')
            for key, values in data.items():
                print(f'{key}: {values[0]}')
            print('===================\n')

            # отвечаем пользователю страницей контактов
            self._send_html('contacts.html', status=200)
        except Exception as e:
            print('Ошибка при обработке POST:', e)
            self._send_html('500.html', status=500)

    def log_message(self, format, *args):
        """Отключаем стандартный лог http.server (чтобы не шумел)."""
        pass


def run() -> None:
    # гарантируем, что читаем файлы рядом с server.py
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    server = HTTPServer((HOST, PORT), MyHandler)
    print(f'Сервер запущен: http://{HOST}:{PORT}')
    print('Ctrl+C — остановить.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nСервер остановлен.')
        server.server_close()


if __name__ == '__main__':
    run()
