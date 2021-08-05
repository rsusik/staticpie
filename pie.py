#!/usr/bin/env python

import argparse, os, sys
import queue
import importlib
import functools
from functools import partial
import threading
from io import BytesIO
import urllib, sys, os, datetime
from http import HTTPStatus
import asyncio
import websockets
import http.server
import socketserver
import email.utils
import webbrowser

import yaml
import psutil
from rich.traceback import install
install(show_locals=True)

from rich import print as rprint
from rich.panel import Panel

import logging
from rich.logging import RichHandler

logging.basicConfig(
    #level="NOTSET",
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")

import core.generator
importlib.reload(core.generator)
from core.generator import ConfigType, Generator

from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler


class LiveReloadHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    live_reload_js_script = b'''
    <script type="text/javascript">
        // This part is copied and modified from below address:
        // https://github.com/ritwickdey/vscode-live-server/blob/master/lib/live-server/injected.html (last checked: 2021-06-03)
        // <![CDATA[  <-- For SVG support
        if ('WebSocket' in window) {
            (function () {
                function refreshCSS() {
                    var sheets = [].slice.call(document.getElementsByTagName("link"));
                    var head = document.getElementsByTagName("head")[0];
                    for (var i = 0; i < sheets.length; ++i) {
                        var elem = sheets[i];
                        var parent = elem.parentElement || head;
                        parent.removeChild(elem);
                        var rel = elem.rel;
                        if (elem.href && typeof rel != "string" || rel.length == 0 || rel.toLowerCase() == "stylesheet") {
                            var url = elem.href.replace(/(&|\?)_cacheOverride=\d+/, '');
                            elem.href = url + (url.indexOf('?') >= 0 ? '&' : '?') + '_cacheOverride=' + (new Date().valueOf());
                        }
                        parent.appendChild(elem);
                    }
                }
                var socket = new WebSocket("ws://{server_host}:{server_port}/");//address
                socket.onmessage = function (msg) {
                    if (msg.data == 'reload') window.location.reload();
                    else if (msg.data == 'refreshcss') refreshCSS();
                };
            })();
        }
        else {
            console.error('ERROR: Your browser does NOT support WebSockets.');
        }
        // ]]>
    </script>
    '''

    def __init__(self, *args, directory, websockets_host, websockets_port, **kwargs):
        self.websockets_host = websockets_host
        self.websockets_port = websockets_port
        super().__init__(*args, directory=directory, **kwargs)

    # The below function is taken from cpython implementation and modified:
    # https://github.com/python/cpython/blob/main/Lib/http/server.py (last checked: 2021-06-03)
    def send_head(self):
        """Common code for GET and HEAD commands.
        This sends the response code and MIME headers.
        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.
        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            if not parts.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                new_parts = (parts[0], parts[1], parts[2] + '/',
                             parts[3], parts[4])
                new_url = urllib.parse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        # check for trailing "/" which should return 404. See Issue17324
        # The test for this was added in test_httpserver.py
        # However, some OS platforms accept a trailingSlash as a filename
        # See discussion on python-dev and Issue34711 regarding
        # parsing and rejection of filenames with a trailing slash
        if path.endswith("/"):
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        try:
            fs = os.fstat(f.fileno())
            # Use browser cache if possible
            if ("If-Modified-Since" in self.headers
                    and "If-None-Match" not in self.headers):
                # compare If-Modified-Since and time of last file modification
                try:
                    ims = email.utils.parsedate_to_datetime(
                        self.headers["If-Modified-Since"])
                except (TypeError, IndexError, OverflowError, ValueError):
                    # ignore ill-formed values
                    pass
                else:
                    if ims.tzinfo is None:
                        # obsolete format with no timezone, cf.
                        # https://tools.ietf.org/html/rfc7231#section-7.1.1.1
                        ims = ims.replace(tzinfo=datetime.timezone.utc)
                    if ims.tzinfo is datetime.timezone.utc:
                        # compare to UTC datetime of last modification
                        last_modif = datetime.datetime.fromtimestamp(
                            fs.st_mtime, datetime.timezone.utc)
                        # remove microseconds, like in If-Modified-Since
                        last_modif = last_modif.replace(microsecond=0)

                        if last_modif <= ims:
                            self.send_response(HTTPStatus.NOT_MODIFIED)
                            self.end_headers()
                            f.close()
                            return None

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", ctype)
            #self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            content = f.read()

            # server_host = self.server.server_address[0]
            # server_port = self.server.server_address[1]
            #client_host = self.client_address[0]
            #client_port = self.client_address[1]

            live_reload_js_script_str = self.live_reload_js_script.replace(
                b'{server_host}', bytes(str(self.websockets_host), encoding='utf-8')).replace(
                b'{server_port}', bytes(str(self.websockets_port), encoding='utf-8')
            )

            content = content.replace(b'</body>', live_reload_js_script_str + b'</body>')

            return BytesIO(content)
        except:
            f.close()
            raise

def serve_http(http_host="localhost", http_port=8080, http_folder='./', websockets_host='localhost', websockets_port=8012):
    Handler = functools.partial(
        LiveReloadHTTPRequestHandler, 
        directory=http_folder,
        websockets_host=websockets_host,
        websockets_port=websockets_port
    )
    with socketserver.TCPServer((http_host, http_port), Handler) as httpd:
        log.info(f'Serving at http://{http_host}:{http_port}')
        httpd.serve_forever()


def generate(config):
    try:
        importlib.reload(core.generator)
        from core.generator import Generator
        generator = Generator(config)
        generator.generate()
    except Exception as ex:
        log.error(f'ERROR: {ex}')


async def remove_disconnected(clients):
    to_remove = list(filter(lambda client: client.closed  == True, clients))
    try:
        while True:
            client = to_remove.pop()
            log.debug(f"Removing {client}")
            clients.remove(client)
    except IndexError:
        log.debug("Success")


def ws_handler(queue, clients):
    async def fun(websocket, path):
        clients.append(websocket)
        while True:
            await asyncio.sleep(1)
            while len(queue) > 0:
                await remove_disconnected(clients) # remove clients with closed connection
                msg = queue.pop()
                log.debug(f'Sending to clients: {msg}')
                for idx, client in enumerate(clients):
                    log.debug(f'Sending to client no. {idx}')
                    await client.send(msg)
    return fun


class FileObserver(object):
    def __init__(self, event_handler, directory='./'):
        self.observer = PollingObserver()
        self.observer.schedule(event_handler(observer=self.observer), directory, recursive=True)

    def __enter__(self):
        self.observer.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.observer.stop()
        self.observer.join()
        return True


class FSEventHandler(FileSystemEventHandler):
    """Logs all the events captured."""

    def __init__(self, observer, queue, clients, config):
        super().__init__()
        self.config  = config
        self.queue   = queue
        self.clients = clients
        self.observer = observer

    def _generate_all(self):
        log.info('Generating all pages from scratch...')
        generate(self.config)
        # Anything that has been triggered dugin generation is removed from queue
        self.observer.event_queue.queue.clear()
        #self.observer.event_queue.task_done()
        log.info('...done.')

    def client_reload(self):
        if len(self.clients) > 0:
            self.queue.append('reload')

    def client_refreshcss(self):
        if len(self.clients) > 0:
            self.queue.append('refreshcss')

    @NotImplementedError
    def _regenerate_one(self):
        # Here only one file is genenerated.
        # The case when only markdown content is modified.
        # Other properties (yaml) may cause the need to generate all
        #print('Regenerating only one file...')
        pass

    def on_moved(self, event):
        super().on_moved(event)
        what = 'directory' if event.is_directory else 'file'
        self._generate_all()
        #self.queue.append(f'{what}, from: {event.src_path} to: {event.dest_path}')

    def on_created(self, event):
        super().on_created(event)
        what = 'directory' if event.is_directory else 'file'
        self._generate_all()
        #self.queue.append(f'{what}, {event.src_path}')

    def on_deleted(self, event):
        super().on_deleted(event)
        # remove from all menus and all references
        # the easiest -> generate everything
        what = 'directory' if event.is_directory else 'file'
        self._generate_all()
        #self.queue.append(f'{what}, {event.src_path}')

    def on_modified(self, event):
        super().on_modified(event)
        what = 'directory' if event.is_directory else 'file'
        log.info(f'Modified, {what}, {event.src_path}')
        log.debug(f'self.config["PUBLIC_FOLDER"]: {self.config["PUBLIC_FOLDER"]}')
        log.debug(f'event.src_path              : {event.src_path}')
        if self.config["PUBLIC_FOLDER"] in event.src_path:
            return
        if what == 'file':
            filename, file_extension = os.path.splitext(event.src_path)
            file_extension = file_extension.lower()
            if file_extension in ['.md']:
                if 'yaml_modified': # TODO
                    self._generate_all()
                    self.client_reload()
                else: # only markdown
                    self._regenerate_one()
                    self.client_reload()
            elif file_extension in ['.css']:
                # copy file to public folder
                # TODO
                # and then refresh css for clients
                self.client_refreshcss()
            elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
                # only reload clients
                self.client_reload()
            else:
                self._generate_all()
                self.client_reload()
        #self.queue.append(f'{what}, {event.src_path}')
        self.observer.event_queue.queue.clear()


def serve_websockets(config, host='127.0.0.1', port=8011):
    msg_queue = []
    clients = []
    FSEventHandlerClass = partial(FSEventHandler, queue=msg_queue, clients=clients, config=config)

    with FileObserver(FSEventHandlerClass, config['ROOT_FOLDER']):
        new_loop = asyncio.new_event_loop()
        start_server = websockets.serve(ws_handler(msg_queue, clients), host, port, loop=new_loop)
        log.info(f'Starting file observer {host}, {port}')
        new_loop.run_until_complete(start_server)
        new_loop.run_forever()


def is_port_open(http_host, http_port):
    return not int(http_port) in [i.laddr.port for i in psutil.net_connections()]
    # import socket
    # a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # socket.setdefaulttimeout(2.0)
    # location = (http_host, int(http_port))
    # result_of_check = a_socket.connect_ex(location)
    # a_socket.close()
    # if result_of_check == 0:
    #     return True
    # else:
    #     return False


def serve(
    http_host : str, 
    http_port : str,
    http_folder : str,
    websockets_host : str,
    websockets_port : str,
    config : core.generator.ConfigType
):
    for _ in range(3):
        if is_port_open(http_host, http_port):
            log.info(f'Port {http_port} for http is open.')
            break
        log.warning(f'Port {http_port} is already in use, trying another one...')
        http_port = int(http_port) + 1

    for _ in range(3):
        if is_port_open(websockets_host, websockets_port):
            log.info(f'Port {websockets_port} for websocket is open.')
            break
        log.warning(f'Port {websockets_port} is already in use, trying another one...')
        websockets_port = int(websockets_port) + 1

    config['BASE_URL'] = f'{http_host}:{http_port}'

    generator = Generator(config)
    generator.generate()

    th2 = threading.Thread(target=serve_http, args=[http_host, http_port, http_folder, websockets_host, websockets_port]) # serve_http(http_host, http_port, http_folder, websockets_host, websockets_port)
    th2.start()

    th = threading.Thread(target=serve_websockets, args=[config, websockets_host, websockets_port]) # serve_websockets(config)
    th.start()

    webbrowser.open(f'http://{http_host}:{http_port}')

    rprint(Panel(f'[bold green]Serving at: http://{http_host}:{http_port}'))


def deploy(
    config : core.generator.ConfigType,
    path : str = None
):
    if path is not None:
        config['PUBLIC_FOLDER'] = path
    generator = Generator(config)
    generator.generate()


def main():
    parser = argparse.ArgumentParser(
        description='Runs the framework in edit mode.',
        #epilog="Example:\npython generate.py --config dev.yaml"
    )

    # GLOBAL ARGUMENTS
    parser.add_argument("action", type=str, help="action", choices=["deploy", "serve"])
    parser.add_argument("-c", "--config", dest='c', type=str, help="config file", default='azmp/azmp.yaml')

    #subparsers = parser.add_subparsers(help='action', dest='action')

    # SERVE
    #parser_serve = subparsers.add_parser('serve', help='serve the website')
    parser_serve = parser
    parser_serve.add_argument("-p", "--port", dest='port', type=str, help="port", default='8080')
    parser_serve.add_argument("-a", "--address", dest='address', type=str, help="address", default='localhost')

    # DEPLOY
    #parser_deploy = subparsers.add_parser('deploy', help='generate the website')
    parser_deploy = parser
    parser_deploy.add_argument("-d", "--directory", dest='dir', type=str, help="deploy folder")
    
    args = parser.parse_args()
    config_path  = args.c

    # LOAD CONFIG FILE
    if os.path.isfile(config_path) != True:
        log.error(f"ERROR: Config file does not exists {config_path}")
        exit(101)
    with open(config_path, 'rt') as f:
        config_str = f.read()

    config = yaml.load(config_str, Loader=yaml.Loader)

    if args.action == 'serve':
        serve(
            args.address,
            int(args.port),
            config["PUBLIC_FOLDER"],
            'localhost',
            8011,
            config
        )
    elif args.action == 'deploy':
        deploy(
            config,
            args.dir
        )
      
    
if __name__ == "__main__":
    main()