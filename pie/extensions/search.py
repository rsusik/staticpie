'''
Performs preprocessing and postprocessing of website.
'''

from collections import defaultdict
from re import split
import lxml.html
import json

class Extension:
    def __init__(self):
        pass

    def preprocessing(self, generator, config, files):
        translation = {
            ord(ch):' '
            for ch in '#![]-><+=@$%^&*()©/?0123456789.",\\\'{};\n\r'
        }

        remove_polish_translation = ''.maketrans('ąćęłńóśżź', 'acelnoszz', '')

        search_pages = []
        for file in files:
            content = (
                ' '.join(set(
                    lxml.html
                    .document_fromstring(file['content'])
                    .text_content().strip().lower()
                    .translate(translation)
                    .translate(remove_polish_translation)
                    .split()
                ))
            ) if 'content' in file and file['content'].strip() != '' else ''
            search_pages.append({
                "url"    : config['PROTOCOL'] + file['meta']['route'],
                'title'  : file['meta']['title'],
                'author' : file['meta']['author'] if 'author' in file['meta'] else '',
                'summary': file['meta']['summary'] if 'summary' in file['meta'] else '',
                'content': content
            })

        with open(f'{config["PUBLIC_FOLDER"]}/search.json', 'wt') as f:
            json.dump(search_pages, f)

        # inv_idx = defaultdict(set)

        # for file in files:
        #     words = set(lxml.html.document_fromstring(file['content']).text_content().translate(translation).lower().split())
        #     for word in words:
        #         inv_idx[word].add(file['meta']['title'])

    

    def on_generation_end(self, generator, config, files):
        # map(lambda x: {
        #     'route': x['route'],
        #     'title': x['title'],
        #     'author': x['author'] if 'author' in x else '',
        #     'summary': x['summary'] if 'summary' in x else '',
        #     'content': x['content'] if 'content' in x else '',
        #     'words': x['content'].split() if 'content' in x else '',
        # })
        pass