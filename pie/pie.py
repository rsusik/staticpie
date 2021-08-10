#!/usr/bin/env python

__version__ = '0.4.2'

import sys

if sys.version_info.major !=3 or sys.version_info.minor < 8:
    print('\033[41m', end='')
    print('=========================> ERROR <=============================')
    print('>       The minimum supported Python version is 3.8.          <')
    print('>          Please install it and then try again.              <')
    print('===============================================================\033[0m')
    exit(1)

import os
import shutil
from pathlib import Path
from functools import partial
import threading
import argparse
import datetime
from typing import Dict, TypedDict
import webbrowser

from rich import print as rprint
from rich.panel import Panel

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
    #http_folder : str,
    websockets_host : str,
    websockets_port : str,
    generator : Generator
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

    generator.generate(
        BASE_URL = f'{http_host}:{http_port}'
    )

    th2 = threading.Thread(target=server.serve_http, args=[http_host, http_port, generator.config['PUBLIC_FOLDER'], websockets_host, websockets_port]) # serve_http(http_host, http_port, http_folder, websockets_host, websockets_port)
    th2.start()

    th = threading.Thread(target=server.serve_websockets, args=[generator, websockets_host, websockets_port]) # serve_websockets(config)
    th.start()

    webbrowser.open(f'http://{http_host}:{http_port}')

    return {
        'status': True,
        'http_host': http_host,
        'http_port': http_port,
        #'http_folder': http_folder,
        'websockets_host': websockets_host,
        'websockets_port': websockets_port,
        'generator': generator,
    }


def deploy(
    generator : Generator,
    path : str = None
):
    args = {}
    if path is not None:
        args['PUBLIC_FOLDER'] = path
    return generator.generate(**args)

import yaml
def _valid_yaml_file(filename):
    with open(filename, 'r') as f:
        try:
            yaml.load(f, Loader=yaml.Loader)
            return True
        except yaml.YAMLError as exception:
            return False


def _get_config_path(
    args
) -> Path:
    config_path  = args.c
    if config_path is None:
        log.debug('No config file was given.')
        cwd = Path(os.getcwd())
        tmp = cwd / Path(f'{cwd.parts[-1]}.yaml')
        if tmp.is_file():
            log.debug(f'Found config file in current working directory {tmp}.')
            config_path = tmp
        else:
            log.error(f'There is no config file in current working directory.')
            exit(104)

    config_path = Path(config_path)
    
    if (
        config_path.exists() == True and 
        config_path.is_file() == True and 
        _valid_yaml_file(config_path) == True
    ):
        log.info(f'Found config file in {config_path}.')
        return Path(config_path)
    elif (
        config_path.exists() == True and 
        config_path.is_dir() == True
    ):
        config_path = config_path / f'{config_path.parts[-1]}.yaml'
        if (
            config_path.exists() == True and 
            config_path.is_file() == True and 
            _valid_yaml_file(config_path) == True
        ):
            log.info(f'Found config file in {config_path}.')
            return Path(config_path)
        else:
            log.error(f'No config file found.')
            exit(104)
    else:
        log.error(f'Config file doesn\'t exists or is NOT a valid yaml file ({config_path})')
        exit(104)


def deploy_action(
    args
) -> None:
    generator = Generator(_get_config_path(args))
    if deploy(
        generator,
        args.dir
    ) == True:
        rprint(Panel(f"[bold green]Success: the website is generated in {generator.config['PUBLIC_FOLDER']} folder.\nYou can upload the content to HTTP server.", title="Summary"))
      

def serve_action(
    args
) -> None:
    generator = Generator(_get_config_path(args))
    serve_out = serve(
        args.address,
        int(args.port),
        'localhost',
        8011,
        generator
    )
    if serve_out['status'] == True:
        rprint(Panel(f"[bold green]Serving at: http://{serve_out['http_host']}:{serve_out['http_port']}", title="Summary"))
    else:
        rprint(Panel(f"[bold red]Error occured, exiting.", title="Summary"))

def _copy_website(
    src : str, 
    dst : str, 
    website_name : str
) -> str:
    dst = dst.replace('{{website_name}}', website_name)
    log.debug(f'Copy {src} to {dst}')
    return shutil.copy2(src, dst)

def create_website_action(
    args
) -> None:
    root_folder = Path(args.dest).absolute()
    if root_folder.exists():
        log.error(f'Path already exists {root_folder}')
        exit(102)

    log.info(f'Creating website in {root_folder}')
    copy_from = Path(__loader__.path).parent / 'assets' / '{{website_name}}'
    copy_to   = root_folder
    website_name = root_folder.parts[-1]

    shutil.copytree(copy_from, copy_to, copy_function=partial(_copy_website, website_name=website_name))

def create_page_action(
    args
) -> None:
    config_path = _get_config_path(args)
    root_folder = config_path.parent
    page_name = args.name
    log.debug(locals())

    log.info(f'Creating page in {root_folder}')
    copy_from = Path(__loader__.path).parent / 'assets' / '{{page}}.md'
    copy_to = root_folder / f'{page_name}.md'
    if copy_to.exists():
        log.error(f'File already exists {copy_to}')
    
    with open(copy_from, 'rt') as f_in, open(copy_to, 'wt') as f_out:
        content = f_in.read()
        content = (
            content
            .replace('{{page_name}}', page_name)
            .replace('{{date}}', datetime.date.today().strftime('%Y-%m-%d'))
        )
        f_out.write(content)
    log.info(f'Page created, {copy_to}')


def main():
    
    parser = argparse.ArgumentParser(
        description='Piece of cake. Static site generator.', 
        prog='pie',
        epilog='''\
Example:
pie create website mywebsite
pie serve mywebsite/mywebsite.yaml\
''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(help='Action', dest='action', required=True)

    # Serve
    parser_serve = subparsers.add_parser('serve', help='Run server')
    parser_serve.add_argument('-p', '--port', dest='port', type=str, help='Port', default='8080')
    parser_serve.add_argument('-c', '--config', dest='c', type=str, help='Config file')
    parser_serve.add_argument('-a', '--address', dest='address', type=str, help='Address', default='localhost')
    parser_serve.set_defaults(func=serve_action)

    # Deploy
    parser_deploy = subparsers.add_parser('deploy', help='Generate the website')
    parser_deploy.add_argument('-c', '--config', dest='c', type=str, help='Config file')
    parser_deploy.add_argument('-d', '--directory', dest='dir', type=str, help='Deploy folder')
    parser_deploy.set_defaults(func=deploy_action)

    # Create
    parser_create = subparsers.add_parser('create', help='Create website/element')
    parser_create_subparsers = parser_create.add_subparsers(help='Entity name', dest='entity', required=True)

    # Create -> website
    parser_create_subparsers_website = parser_create_subparsers.add_parser('website', help='Create website in given folder')
    parser_create_subparsers_website.add_argument(dest='dest', type=str, help="Path for new website files")
    parser_create_subparsers_website.set_defaults(func=create_website_action)

    # Create -> page
    parser_create_subparsers_page = parser_create_subparsers.add_parser('page', help='Create page in given directory')
    parser_create_subparsers_page.add_argument(dest='name', type=str, help="Page name (also the md filename)")
    parser_create_subparsers_page.add_argument('-c', '--config', dest='c', type=str, help='Config file')
    parser_create_subparsers_page.set_defaults(func=create_page_action)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()