import os
import json
from typing import Dict, List, TypedDict

from pie.core.generator import (
    Generator, 
    ConfigType,
    FileStartType,
    FilePreType,
    FilePostType,
    FileEndType
)
from pie.core.extension import Extension
from . import default_conf


class TagsExtension(Extension):
    def on_generation_start(self, 
        generator : Generator,
        files : List[FileStartType]
    ):
        if 'tags' not in generator.config:
            generator.config['tags'] = {}
        if 'tags_ignored' not in generator.config['tags']:
            generator.config['tags']['tags_ignored'] = default_conf.tags_ignored
        if 'tags_map' not in generator.config['tags']:
            generator.config['tags']['tags_map'] = default_conf.tags_map

        generator.config["tags"] = {
            **generator.config["tags"],
            'tags': self.get_all_tags(
                files,
                generator.config['tags']['tags_ignored'],
                generator.config['tags']['tags_map']
            ),
            'pages': self.get_all_pages_with_tags(
                files
            )
        }

        js_folder = f'{generator.config["PUBLIC_FOLDER"]}/js'
        os.makedirs(js_folder, exist_ok=True)

        with open(f'{js_folder}/tags.js', 'wt') as f:
            f.write(f'var tags = {json.dumps(generator.config["tags"])}')


    def get_all_tags(
        self, 
        files : List[FileStartType],
        tags_ignored : List[str],
        tags_map : Dict[str, TypedDict('', {'label': str, 'order': int})]
    ):
        tags = {}
        for file in files:
            if 'tags' in file['meta']:
                for tag in file['meta']['tags']:
                    if tag in tags:
                        tags[tag]['count'] += 1
                        tags[tag]['related'] = tags[tag]['related'].union( set(file['meta']['tags']) - {tag} )
                    else:
                        tags[tag] = {
                            'count': 1,
                            'related': set(file['meta']['tags']) - {tag}
                        }
        
        proper_tags = dict(filter(lambda x: x[0] not in tags_ignored, tags.items()))
        tmp = list(map(lambda el: ({
            'tag': el[0],
            'label': tags_map[el[0]]['label'] if el[0] in tags_map else el[0],
            'order': tags_map[el[0]]['order'] if el[0] in tags_map else 999,
            'count': el[1]['count'],
            'related': list(el[1]['related'])
        }), proper_tags.items()))
        
        proper_tags = sorted(tmp, key = lambda x: (x['order'], x['count'], x['label']))

        return proper_tags


    def get_all_pages_with_tags(
        self, 
        files : List[FileStartType],
    ):
        pages = []
        for file in files:
            if 'tags' in file['meta']: # if that page should be considered
                pages.append({
                    #'filename': filename,
                    'title': file['meta']['title'],
                    'date': file['meta']['date'].strftime('%Y-%m-%dT%H:%M:%S') if 'date' in file['meta'] else None,
                    'summary': file['meta']['summary'] if 'summary' in file['meta'] else '',
                    'route': file['meta']['route'],
                    #'author': tmp_page_conf['author'] if 'author' in tmp_page_conf else '',
                    'tags': file['meta']['tags']
                })
        return pages

