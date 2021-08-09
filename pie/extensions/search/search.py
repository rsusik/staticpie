import lxml.html
import json
from typing import List

from pie.core.generator import (
    Generator, 
    ConfigType,
    FileStartType,
    FilePreType,
    FilePostType,
    FileEndType
)
from pie.core.extension import Extension

class SearchExtension(Extension):
    def preprocessing(self, 
        generator : Generator,
        files : List[FilePreType]
    ):
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
                "url"    : generator.config['PROTOCOL'] + file['meta']['route'],
                'title'  : file['meta']['title'],
                'author' : file['meta']['author'] if 'author' in file['meta'] else '',
                'summary': file['meta']['summary'] if 'summary' in file['meta'] else '',
                'content': content
            })

        with open(f'{generator.config["PUBLIC_FOLDER"]}/search.json', 'wt') as f:
            json.dump(search_pages, f)
