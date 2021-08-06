# Dependency: TAGS
import numpy as np
from glob import glob
import yaml
from core.extension import Extension
from extensions.tags_conf import *
import json
import os

# TODO: Przerobić na nową wersję
class TagsExtension(Extension):
    def on_generation_start(self, generator, config, all_files):
        config["ex_tags"] = {
            'tags': self.get_all_tags(all_files),
            'pages': self.get_all_pages_with_tags(all_files)
        }

        js_folder = f'{config["PUBLIC_FOLDER"]}/js'
        os.makedirs(js_folder, exist_ok=True)

        with open(f'{js_folder}/ex_tags.js', 'wt') as f:
            f.write(f'var ex_tags = {json.dumps(config["ex_tags"])}')

    def get_all_tags(self, all_files):
        tags = {}
        for file in all_files:
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
        tmp = list(map(lambda el: ({ # TODO: quite ugly
            'tag': el[0],
            'label': tags_config[el[0]]['label'] if el[0] in tags_config else el[0],
            'order': tags_config[el[0]]['order'] if el[0] in tags_config else 999,
            'count': el[1]['count'],
            'related': list(el[1]['related'])
        }), proper_tags.items()))
        
        proper_tags = sorted(tmp, key = lambda x: (x['order'], x['count'], x['label']))

        return proper_tags

    def get_all_pages_with_tags(self, all_files):
        pages = []
        for file in all_files:
            if 'tags' in file['meta']: # if that page should be considered
                pages.append({
                    #'filename': filename,
                    'title': file['meta']['title'],
                    'date': file['meta']['date'] if 'date' in file['meta'] else None,
                    'summary': file['meta']['summary'] if 'summary' in file['meta'] else '',
                    'route': file['meta']['route'],
                    #'author': tmp_page_conf['author'] if 'author' in tmp_page_conf else '',
                    'tags': file['meta']['tags']
                })
        return pages

    
