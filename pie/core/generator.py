from glob import glob
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader
import markdown
import re
from markdown.extensions import Extension
import yaml
import os, shutil
import importlib
import pickle
import datetime
from time import sleep
from typing import Dict, List, TypedDict # Python 3.8

from pie.core.utils import *

from pathlib import Path
from pie.core.utils import log


class ConfigType(TypedDict):
    ROOT_FOLDER: str
    PUBLIC_FOLDER: str
    BASE_URL: str
    PROTOCOL: str
    includes: List[str]
    extensions: List[str]


class FileMetaType(TypedDict, total=False):
    route: str
    title: str
    template: str
    author: str
    summary: str
    date: str

class FileType(TypedDict):
    filename: str
    content: str

class FileStartType(FileType):
    meta: FileMetaType

class FilePreType(FileType):
    meta: FileMetaType

class FilePostType(FileType):
    meta: FileMetaType

class FileEndType(FileType):
    meta: FileMetaType
    dest_filename: str
    dest_folder: str


class WrongMarkdownFileException(Exception):
    def __init__(self, filename=None, markdown=None):
        self.filename = filename
        self.markdown = markdown
        if self.filename is not None:
            self.message = f'ERROR: Markdown file is wrong ({self.filename})'
        else:
            self.message = f'ERROR: Markdown is wrong.'
        super().__init__(self.message)


class Generator:
    def __init__(self, config_path : str) -> None: # config : ConfigType
        self.config_path = config_path
        self.config : ConfigType = self.load_config_file(config_path)
        self.config['GENERATION_TIME'] = datetime.date.today().strftime('%Y-%m-%d')


    @staticmethod
    def load_config_file(config_path : str) -> ConfigType:
        if os.path.isfile(config_path) != True:
            log.error(f"Config file does not exists {config_path}")
            exit(101)

        with open(config_path, 'rt') as f:
            config_str = f.read()

        config : ConfigType = yaml.load(config_str, Loader=yaml.Loader)

        if 'includes' not in config:
            config['includes'] = []

        if 'extensions' not in config:
            config['extensions'] = []

        config['ROOT_FOLDER'] = os.path.dirname(config_path)

        return config

    # Function that injects config constants into template/content
    def _inject_constants(self, constants, content):
        for key, value in constants.items():
            if isinstance(value, str) or str(value).replace('.','',1).isnumeric():
                content = content.replace(f'~~{key}~~', value)
        return content
    

    def get_md_files(self):
        return [f for f in glob(f'{self.config["ROOT_FOLDER"]}/*.md')] + [f for f in glob(f'{self.config["ROOT_FOLDER"]}/+*/*.md')]
    

    def read_markdown_string(self, md_string):
        md_string = f'\n{md_string}'
        anchors = list(re.finditer('\r?\n-+\r?\n', md_string))
        if len(anchors) >= 2:
            meta = md_string[anchors[0].end():anchors[1].start()]
            content = md_string[anchors[1].end():]
        else:
            raise WrongMarkdownFileException
        return (content, meta)
    

    def read_markdown_file(self, md_filename):
        try:
            with open(md_filename, 'rt') as f:
                md_string = f.read()
                return self.read_markdown_string(md_string)
        except WrongMarkdownFileException as ex:
            raise WrongMarkdownFileException(md_filename)


    def module_exists(self, module_name : str):
        try:
            __import__(module_name)
            return True
        except ModuleNotFoundError as ex:
            if ex.name == module_name or ex.name == '.'.join(module_name.split('.')[0:-1]):
                return False
            else:
                raise ex


    def _get_extension_class(self, module):
        extension_class_name = [xx for xx in module.__dict__ if 'Extension' in xx][-1]
        extension_class = getattr(module, extension_class_name)
        return extension_class()


    def _has_extension_class(self, module):
        extension_class_name = [xx for xx in module.__dict__ if 'Extension' in xx]
        if len(extension_class_name) > 0:
            return True
        else:
            return False
        

    def _get_extension_class_from_file(self, extension_filename : str):
        spec = importlib.util.spec_from_file_location('', extension_filename)
        ext = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ext)
        return self._get_extension_class(ext)

    
    def get_extensions(self) -> List[Extension]:
        extensions = []
        if 'extensions' in self.config:
            for module_name in self.config['extensions']:
                log.debug(f'Processing: {module_name.lower()}')
                # Check if extension is in installed modules
                if self.module_exists(module_name.lower()):
                    module_tmp = __import__(module_name.lower(), fromlist=[None]) # load module
                    extensions.append(self._get_extension_class(module_tmp))
                    continue
                # Check if extension is in built-in extensions
                if self.module_exists(f'pie.extensions.{module_name.lower()}'):
                    log.debug(f'Loading module: pie.extensions.{module_name.lower()}')
                    module_tmp = __import__(f'pie.extensions.{module_name.lower()}', fromlist=['']) # load module
                    if self._has_extension_class(module_tmp):
                        extensions.append(self._get_extension_class(module_tmp))
                        continue
                    else: # maybe it is in folder
                        module_tmp = __import__(f'pie.extensions.{module_name}.{module_name}', fromlist=[''])
                        if self._has_extension_class(module_tmp):
                            extensions.append(self._get_extension_class(module_tmp))
                            continue
                        else:
                            log.warning(f'There is no extension class in `{module_tmp.__dict__["__name__"]}` module.')
                    
                # Check if extension is in website root folder
                extension_filename = f'{self.config["ROOT_FOLDER"]}/extensions/{module_name}'
                if Path(f'{extension_filename}.py').is_file():
                    extension_filename = f'{extension_filename}.py'
                    extensions.append(self._get_extension_class_from_file(extension_filename))
                    continue
                elif Path(extension_filename).is_dir() and Path(extension_filename) / f'{Path(extension_filename).stem}.py':
                    extension_filename = Path(extension_filename) / f'{Path(extension_filename).stem}.py'
                    extensions.append(self._get_extension_class_from_file(extension_filename))
                    continue
                # If any above then error
                log.error(f'Unrecognized extension: {module_name}')
        return extensions


    def md2html(self, md):
        converter = markdown.Markdown(
            extensions=[
                # TODO: Przenieść do pliku konfiguracyjnego
                'toc',
                'fenced_code',
                'codehilite',
                'markdown.extensions.footnotes',
                'markdown.extensions.attr_list',
                'markdown.extensions.def_list',
                'markdown.extensions.tables',
                'markdown.extensions.abbr',
                'markdown.extensions.md_in_html'
                # The below extensions come from: https://facelessuser.github.io/pymdown-extensions/extensions/arithmatex/
                #'pymdownx.tabbed' # doesn't work properly with bootstrap
                ,'pymdownx.arithmatex' # mathJax
                ,'pymdownx.caret' # superscript -> text^a\ superscript^
                ,'pymdownx.details'
                #,'pymdownx.emoji'
                #,'pymdownx.escapeall' # lets escape all characters like: \W\e\ \c\a\n\ \e\s\c\a\p\e
                ,'pymdownx.highlight' # syntax highlighting, adds class "language-{language}"
                ,'pymdownx.keys' # easily type keyboard shortcuts: ++ctrl+alt+delete++
                ,'pymdownx.magiclink' # automatically puts links: <a href="..">
                ,'pymdownx.mark' # marks a text
                #,'pymdownx.progressbar' # doesn't work properly with bootstrap [=25% "25%"]
                ,'pymdownx.superfences' # I didn't check it
                ,'pymdownx.tasklist' # task list such as - [x]
                ,'pymdownx.tilde' # allow writting: ~~Delete me~~ or text~a\ subscript~
            ],
            extension_configs={
                "pymdownx.arithmatex": {
                    'smart_dollar': False,
                    'preview': False
                },
                'codehilite': {
                    'use_pygments': False
                }
            }
        )

        html = converter.convert(md)
        toc = converter.toc_tokens

        html = (
            html
            .replace('<table>', '<table class="table table-striped table-hover">')
            .replace('th align="center"', 'th style="text-align: center"')
            .replace('th align="right"', 'th style="text-align: right"')
        )
        return html, toc


    def generate(self, **kwargs):
        self.config = {
            **self.config,
            **kwargs
        }
        with console.status('[bold green] Generating...'):
            template_env = Environment(loader=FileSystemLoader(f'{self.config["ROOT_FOLDER"]}/'))
            shutil.rmtree(f'{self.config["PUBLIC_FOLDER"]}', ignore_errors=True)
            for incl in self.config['includes']:
                if os.path.isdir(f'{self.config["ROOT_FOLDER"]}/{incl}'):
                    shutil.rmtree(f'{self.config["PUBLIC_FOLDER"]}/{incl}', ignore_errors=True)
                    shutil.copytree(f'{self.config["ROOT_FOLDER"]}/{incl}', f'{self.config["PUBLIC_FOLDER"]}/{incl}') # , dirs_exist_ok=True
                else:
                    shutil.copy(f'{self.config["ROOT_FOLDER"]}/{incl}', f'{self.config["PUBLIC_FOLDER"]}/{incl}')

            # ==================== STAGE 1 ========================
            # Read all files and store in list (meta is dictionary)
            # =====================================================
            md_files = self.get_md_files()
            self.all_files = []
            for md_file in md_files:
                content_str, meta_str = self.read_markdown_file(md_file)

                meta_raw = yaml.load(meta_str, Loader=yaml.Loader)

                #meta_hash = hashlib.md5(meta_str.encode()).hexdigest()
                #content_hash = hashlib.md5(content_str.encode()).hexdigest()

                self.all_files.append({
                    'filename': md_file,
                    # 'meta_hash': meta_hash,
                    # 'content_hash': content_hash,
                    'content': content_str,
                    'meta': meta_raw
                })

            # Execute on_generation_start (global extensions)
            for extension in self.get_extensions():
                on_generation_start = getattr(extension, 'on_generation_start', None)  
                if on_generation_start is not None:
                    extension.on_generation_start(self, self.all_files)

            console.log('[blue]Stage 1.  [/blue] Read *.md files: [green]COMPLETE[/green]')

            # ==================== STAGE 2 ========================
            # Inject constants into the meta and content
            # =====================================================
            for file in self.all_files:
                file['meta'] = {
                    key:self._inject_constants(self.config, value) if isinstance(value, str) else value 
                    for key, value in file['meta'].items()
                }
                file['content'] = self._inject_constants(self.config, file['content'])

            for extension in self.get_extensions():
                preprocessing = getattr(extension, 'preprocessing', None)  
                if preprocessing is not None:
                    extension.preprocessing(self, self.all_files)

            console.log('[blue]Stage 2.  [/blue] Preprocessing: [green]COMPLETE[/green]')

            # ==================== STAGE 3 ============================
            # Combine template and markdown., generate HTML, create TOC
            # =========================================================
            for file in self.all_files:
                file['meta'] = file['meta']
                # TODO: Generowanie HTMLa / parsowanie markdowna
                body, toc = self.md2html(file['content'])
                file['meta']['toc'] = toc

                # Processing template file
                if 'template' in file['meta']:
                    tpl_filename = f'{self.config["ROOT_FOLDER"]}/' + file['meta']['template']
                elif Path(file['filename'].replace('.md', '.html')).exists():
                    tpl_filename = file['filename'].replace('.md', '.html')
                else:
                    raise Exception(f'ERROR: There is no template for {file["filename"]}')

                if Path(tpl_filename).exists():
                    with open(tpl_filename, 'rt') as f:
                        tpl = f.read()
                else:
                    raise Exception(f'ERROR: There is no template in {tpl_filename}')

                # Generate HTML
                #tpl = self.inject_constants(self.config, tpl)
                template = template_env.from_string(tpl)
                html = template.render({ # process template
                    **{
                        'body': body,
                        'config': self.config,
                        'meta': file['meta']
                    },
                })

                template = template_env.from_string(html)
                html = template.render({ # process template instructions embedded in markdown
                    **{
                    'config': self.config,
                    'meta': file['meta']
                    }
                })
                file['content'] = html

            console.log('[blue]Stage 3.  [/blue] HTML generation: [green]COMPLETE[/green]')

            for extension in self.get_extensions():
                postprocessing = getattr(extension, 'postprocessing', None)  
                if postprocessing is not None:
                    extension.postprocessing(self, self.all_files)

            console.log('[blue]Stage 3.1.[/blue] Postprocessing: [green]COMPLETE[/green]')

            # ==================== STAGE 4 =================
            # Save HTML files in destination directory
            # ==============================================

            for file in self.all_files:
                # get destination folder
                dest_filename = file['meta']['route'].replace(self.config['BASE_URL'], '')
                dest_filename = re.sub(r'^/', '', dest_filename) # remove / from begining
                dest_filename = f'{self.config["PUBLIC_FOLDER"]}/' + dest_filename # add website output path
                if not '.html' in dest_filename: # add index.html if file name is not specified
                    dest_filename += '/index.html'
                dest_folder = os.path.dirname(dest_filename)

                # make dest. directory
                os.makedirs(dest_folder, exist_ok=True)
                
                # save file
                with open(f'{dest_filename}', 'wt') as f:
                    f.write(file['content'])

                file['dest_filename'] = dest_filename
                file['dest_folder'] = dest_folder

            # Execute on_generation_end for each extension
            for extension in self.get_extensions():
                on_generation_end = getattr(extension, 'on_generation_end', None)  
                if on_generation_end is not None:
                    extension.on_generation_end(self, self.all_files)

            
            with open(f'{self.config["PUBLIC_FOLDER"]}/pages.pickle', 'wb') as f:
                pickle.dump(self.all_files, f, pickle.HIGHEST_PROTOCOL)

            console.log('[blue]Stage 4.  [/blue] Finishing tasks: [green]COMPLETE[/green]')

        return True
