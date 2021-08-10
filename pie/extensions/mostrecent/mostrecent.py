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

class MostrecentExtension(Extension):

    def cut(self, str, max_length):
        if len(str) > max_length:
            return str[:max_length] + '...'
        else:
            return str

    def preprocessing(self, 
        generator : Generator, 
        files : List[FilePreType]
    ) -> None:
        
        pages_with_date = filter(lambda x: 'date' in x['meta'], files)
        pages_with_date_sorted = sorted(pages_with_date, key=lambda x: x['meta']['date'], reverse=True)
        pages_with_date_sorted_map = map(lambda file: {
            'title': file['meta']['title'],
            'date': file['meta']['date'],
            'summary': self.cut(file['meta']['summary'], 60) if 'summary' in file['meta'] else '',
            'author': file['meta']['author'] if 'author' in file['meta'] else '',
            'route': file['meta']['route'],
        }, pages_with_date_sorted)

        generator.config['mostrecent'] = list(pages_with_date_sorted_map)

