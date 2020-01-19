# python3

import json
import socket
import sys
from email.parser import Parser
from functools import lru_cache
from urllib.parse import parse_qs, urlparse
import re  # for regulars

MAX_LINE = 64 * 1024
MAX_HEADERS = 100


class Server:
    def __init__(self):
        self._host = '127.0.0.1'
        self._port = 8000
        self._worker = workerTxt("RU.txt")

    def serve_forever(self):
        serv_sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            proto=0)

        try:
            serv_sock.bind((self._host, self._port))
            serv_sock.listen()

            while True:
                conn, _ = serv_sock.accept()
                try:
                    self.serve_client(conn)
                except Exception as e:
                    print('Client serving failed', e)
        finally:
            serv_sock.close()

    def serve_client(self, conn):
        try:
            req = self.parse_request(conn)
            resp = self.handle_request(req)
            self.send_response(conn, resp)
        except ConnectionResetError:
            conn = None
        except Exception as e:
            self.send_error(conn, e)

        if conn:
            req.rfile.close()
            conn.close()

    def parse_request(self, conn):
        rfile = conn.makefile('rb')
        method, target, ver = self.parse_request_line(rfile)
        headers = self.parse_headers(rfile)
        host = headers.get('Host')
        if not host:
            raise HTTPError(400, 'Bad request',
                            'Host header is missing')
        if host not in (self._host,
                        f'{self._host}:{self._port}'):
            raise HTTPError(404, 'Not found')
        return Request(method, target, ver, headers, rfile)

    def parse_request_line(self, rfile):
        raw = rfile.readline(MAX_LINE + 1)
        if len(raw) > MAX_LINE:
            raise HTTPError(400, 'Bad request',
                            'Request line is too long')

        req_line = str(raw, 'iso-8859-1')
        words = req_line.split()
        if len(words) != 3:
            raise HTTPError(400, 'Bad request',
                            'Malformed request line')

        method, target, ver = words
        if ver != 'HTTP/1.1':
            raise HTTPError(505, 'HTTP Version Not Supported')
        return method, target, ver

    def parse_headers(self, rfile):
        headers = []
        while True:
            line = rfile.readline(MAX_LINE + 1)
            if len(line) > MAX_LINE:
                raise HTTPError(494, 'Request header too large')

            if line in (b'\r\n', b'\n', b''):
                break

            headers.append(line)
            if len(headers) > MAX_HEADERS:
                raise HTTPError(494, 'Too many headers')

        sheaders = b''.join(headers).decode('iso-8859-1')
        return Parser().parsestr(sheaders)

    def handle_request(self, req):
        if req.path == '/users' and req.method == 'POST':
            return self.handle_post_users(req)

        if req.path == '/users' and req.method == 'GET':
            return self.handle_get_users(req)

        if req.path == '/towns' and req.method == 'GET':
            return self.handle_get_n_towns_from(req)

        if req.path == '/towns/north' and req.method == 'GET':
            return self.handle_get_norther_town(req)

        if req.path == '/towns/id' and req.method == 'GET':
            return self.handle_get_town_by_id(req)

        if req.path.startswith('/users/'):
            user_id = req.path[len('/users/'):]
            if user_id.isdigit():
                return self.handle_get_user(req, user_id)

        raise HTTPError(404, 'Not found')

    def send_response(self, conn, resp):
        wfile = conn.makefile('wb')
        status_line = f'HTTP/1.1 {resp.status} {resp.reason}\r\n'
        wfile.write(status_line.encode('iso-8859-1'))

        if resp.headers:
            for (key, value) in resp.headers:
                header_line = f'{key}: {value}\r\n'
                wfile.write(header_line.encode('iso-8859-1'))

        wfile.write(b'\r\n')

        if resp.body:
            wfile.write(resp.body)

        wfile.flush()
        wfile.close()

    def send_error(self, conn, err):
        try:
            status = err.status
            reason = err.reason
            body = (err.body or err.reason).encode('utf-8')
        except:
            status = 500
            reason = b'Internal Server Error'
            body = b'Internal Server Error'
        resp = Response(status, reason,
                        [('Content-Length', len(body))],
                        body)
        self.send_response(conn, resp)

    def handle_get_town_by_id(self, req):
        accept = req.headers.get('Accept')
        if 'text/html' in accept:
            contentType = 'text/html; charset=utf-8'
            data = {'id': req.query['id'][0]}
            text = self._worker.get_town_by_id(data['id'])
            body = '<html><head></head><body>'
            body += f'#{text}'
            body += '</body></html>'
        else:
            return Response(406, 'Not Acceptable')
        body = body.encode('utf-8')
        headers = [('Content-Type', contentType),
                   ('Content-Length', len(body))]
        return Response(200, 'OK', headers, body)

    def handle_get_n_towns_from(self, req):
      accept = req.headers.get('Accept')
      if 'text/html' in accept:
        contentType = 'text/html; charset=utf-8'
        data = {'id': req.query['id'][0],
                'n': req.query['n'][0]}
        text = self._worker.get_n_towns_from(data['id'],data['n'])
        body = '<html><head></head><body'
        body += f'<div>Города ({len(text)})</div>'
        body += '<ul>'
        for line in text:
          body += f'<li>#{line}</li>'
        body += '</ul>'
        body += '</body></html>'
      else:
        return Response(406, 'Not Acceptable')
      body = body.encode('utf-8')
      headers = [('Content-Type', contentType),
                 ('Content-Length', len(body))]
      return Response(200, 'OK', headers, body)

    def handle_get_norther_town(self, req):
      accept = req.headers.get('Accept')
      if 'text/html' in accept:
        contentType = 'text/html; charset=utf-8'
        data = {'first': req.query['first'][0],
                'second': req.query['second'][0]}
        text = self._worker.get_norther_town(data['first'], data['second'])
        body = '<html><head></head><body'
        body += f'<div>{text["difference"]}</div>'
        body += '<ul>'
        body += f'<li>Север: {text["north"]}</li>'
        body += f'<li>Юг: {text["south"]}</li>'
        body += '</ul>'
        body += '</body></html>'
      else:
        return Response(406, 'Not Acceptable')
      body = body.encode('utf-8')
      headers = [('Content-Type', contentType),
                 ('Content-Length', len(body))]
      return Response(200, 'OK', headers, body)


class Request:
    def __init__(self, method, target, version, headers, rfile):
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.rfile = rfile

    @property
    def path(self):
        return self.url.path

    @property
    @lru_cache(maxsize=None)
    def query(self):
        return parse_qs(self.url.query)

    @property
    @lru_cache(maxsize=None)
    def url(self):
        return urlparse(self.target)

    def body(self):
        size = self.headers.get('Content-Length')
        if not size:
            return None
        return self.rfile.read(size)


class Response:
    def __init__(self, status, reason, headers=None, body=None):
        self.status = status
        self.reason = reason
        self.headers = headers
        self.body = body


class HTTPError(Exception):
    def __init__(self, status, reason, body=None):
        super()
        self.status = status
        self.reason = reason
        self.body = body


class workerTxt:
    def __init__(self, filename):
        self.filename = filename

    def get_town_by_id(self, id):
        file = open("RU.txt")
        for line in file:
            if (line.startswith(str(id) + '\t')):
                file = open("RU.txt")
                return line.replace(str(id) + '\t', '')
        return "No such town"

    def get_n_towns_from(self, id, count):
        file = open("RU.txt")
        towns = []
        n = 0
        start_count = False
        for line in file:
            if (line.startswith(str(id) + '\t')):
                start_count = True
            if (start_count):
                if (n == count):
                    return towns
                towns.append(re.sub(r'^\d*\t', '', line))
                n += 1
        if (not start_count):
            return "No such town"
        file = open("RU.txt")
        for line in file:
            if (n == count):
                return towns
            towns.append(re.sub(r'^\d*\t', '', line))
            n += 1

    def get_n_towns(self, count):
        file = open("RU.txt")
        towns = []
        for i in range(count):
            towns.append(re.sub(r'^\d*\t', '', file.readline()))
        return towns

    def get_norther_town(self, first, second):
        file = open("RU.txt")
        first_pretenders = []  # номинанты быть первым городом
        second_pretenders = []  # номинанты быть вторым городом
        for line in file:
            info = line.split('\t')
            search = re.search("," + first + r"$", info[3])
            if (search):  # состоит ли первый город в перечислении альтернативных названий города
                first_pretenders.append(info)
            search = re.search("," + second + r"$", info[3])
            if (search):
                second_pretenders.append((info))
        if (not first_pretenders and not second_pretenders):
            return "No such towns"
        if (not first_pretenders):
            return "No such first town"
        if (not second_pretenders):
            return "No such second town"
        if (len(first_pretenders) > 1):
            nice_pretender = first_pretenders[0]
            for pretender in first_pretenders:  # Рассматриваем каждого претендента
                if (pretender[14] > nice_pretender[14]):
                    nice_pretender = pretender
            first_pretenders = [nice_pretender]
        if (len(second_pretenders) > 1):
            nice_pretender = second_pretenders[0]
            for pretender in second_pretenders:  # Рассматриваем каждого претендента
                if (pretender[14] > nice_pretender[14]):
                    nice_pretender = pretender
            second_pretenders = [nice_pretender]
        if (first_pretenders[0][4] >= second_pretenders[0][4]):
            town1 = "\t".join(first_pretenders[0][1:])
            town2 = "\t".join(second_pretenders[0][1:])
        if (second_pretenders[0][4] > first_pretenders[0][4]):
            town1 = "\t".join(second_pretenders[0][1:])
            town2 = "\t".join(first_pretenders[0][1:])
        difference = "Нет временной разницы" if first_pretenders[0][-2] == second_pretenders[0][
            -2] else "Есть временная разница"
        towns = {"north": town1, "south": town2, "difference": difference}
        return towns


if __name__ == '__main__':
    serv = Server()
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        pass
