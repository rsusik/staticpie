#!/usr/bin/env python

__version__ = '0.0.1'

import os, sys
if sys.version_info.major !=3 or sys.version_info.minor < 8:
    print('\033[41m')
    print('=========================> ERROR <=============================')
    print('>       The minimum supported Python version is 3.8.          <')
    print('>          Please install it and then try again.              <')
    print('===============================================================\033[0m')
    exit(1)

import threading
import argparse
from typing import Dict, TypedDict
import webbrowser

import yaml
from rich import box, print as rprint
from rich.panel import Panel
from rich.pretty import pprint

from pie.core.generator import ConfigType, Generator
from pie.core.server import log, is_port_open
from pie.core import server

class ServeArgs(TypedDict, total=False):
    status: bool
    http_host : str
    http_port : str
    http_folder : str
    websockets_host : str
    websockets_port : str
    config : ConfigType

def serve(
    http_host : str, 
    http_port : str,
    http_folder : str,
    websockets_host : str,
    websockets_port : str,
    config : ConfigType
) -> ServeArgs:
    for _ in range(3):
        if is_port_open(http_host, http_port):
            log.info(f'Using port {http_port} for http server.')
            break
        log.warning(f'Port {http_port} is already in use, trying another one...')
        http_port = int(http_port) + 1
    else:
        log.error('All the checked ports for HTTP are already in use.')
        return {'status': False}


    for _ in range(3):
        if is_port_open(websockets_host, websockets_port):
            log.info(f'Using port {websockets_port} for websocket.')
            break
        log.warning(f'Port {websockets_port} is already in use, trying another one...')
        websockets_port = int(websockets_port) + 1
    else:
        log.error('All the checked ports for websocket are already in use.')
        return {'status': False}

    config['BASE_URL'] = f'{http_host}:{http_port}'

    generator = Generator(config)
    generator.generate()

    th2 = threading.Thread(target=server.serve_http, args=[http_host, http_port, http_folder, websockets_host, websockets_port]) # serve_http(http_host, http_port, http_folder, websockets_host, websockets_port)
    th2.start()

    th = threading.Thread(target=server.serve_websockets, args=[config, websockets_host, websockets_port]) # serve_websockets(config)
    th.start()

    webbrowser.open(f'http://{http_host}:{http_port}')

    return {
        'status': True,
        'http_host': http_host,
        'http_port': http_port,
        'http_folder': http_folder,
        'websockets_host': websockets_host,
        'websockets_port': websockets_port,
        'config': config,
    }


def deploy(
    config : ConfigType,
    path : str = None
):
    if path is not None:
        config['PUBLIC_FOLDER'] = path
    generator = Generator(config)
    return generator.generate()


def load_config_file(config_path : str) -> ConfigType:
    # LOAD CONFIG FILE
    if os.path.isfile(config_path) != True:
        log.error(f"Config file does not exists {config_path}")
        exit(101)
    with open(config_path, 'rt') as f:
        config_str = f.read()

    return yaml.load(config_str, Loader=yaml.Loader)


def main():
    parser = argparse.ArgumentParser(
        description='Piece of cake. Static site generator.',
        #epilog="Example:\npython generate.py --config dev.yaml"
    )

    # GLOBAL ARGUMENTS
    parser.add_argument("action", type=str, help="action", choices=["deploy", "serve"])
    parser.add_argument("-c", "--config", required=True, dest='c', type=str, help="config file")

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

    config = load_config_file(config_path)

    if args.action == 'serve':
        serve_out = serve(
            args.address,
            int(args.port),
            config["PUBLIC_FOLDER"],
            'localhost',
            8011,
            config
        )
        if serve_out['status'] == True:
            rprint(Panel(f"[bold green]Serving at: http://{serve_out['http_host']}:{serve_out['http_port']}", title="Summary"))
        else:
            rprint(Panel(f"[bold red]Error occured, exiting.", title="Summary"))
    elif args.action == 'deploy':
        if deploy(
            config,
            args.dir
        ) == True:
            rprint(Panel(f"[bold green]Success: the website is generated in {config['PUBLIC_FOLDER']} folder.\nYou can upload the content to HTTP server.", title="Summary"))
      
    
if __name__ == "__main__":
    main()