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

    def cut(self, str, max_length):
        if len(str) > max_length:
            return str[:max_length] + '...'
        else:
            return str

    def preprocessing(self, generator, config, files):
        
        pages_with_date = filter(lambda x: 'date' in x['meta'], files)
        pages_with_date_sorted = sorted(pages_with_date, key=lambda x: x['meta']['date'])
        pages_with_date_sorted_map = map(lambda file: {
            'title': file['meta']['title'],
            'date': file['meta']['date'],
            'summary': self.cut(file['meta']['summary'], 60) if 'summary' in file['meta'] else '',
            'author': file['meta']['author'] if 'author' in file['meta'] else '',
            'route': file['meta']['route'],
        }, pages_with_date_sorted)

        config['most_recent'] = list(pages_with_date_sorted_map)

