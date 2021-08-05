import numpy as np
from glob import glob
import yaml
from core.extension import Extension
import shutil, os, itertools


template_meta = '''
route: !###!ROUTE!###!
template: tpl_only_body.html
extensions: [plist.py]
plist_tags: !###!TAGS!###!
title: !###!TITLE!###!
author: Robert
'''

template_content = '''
You are at {{ route }}

Articles:

{{plist_pages}}

<ul>
{% for page in meta.plist_pages %}
    <li>
    {{ page.filename }} <br />
    {{ page.meta.title }} <br />
    {{ page.meta.author }} <br />
    {{ page.meta.date }} <br />
    {{ page.meta.summary }} <br />
    <a href="{{page.meta.route}}">{{ page.meta.route }}</a>
    </li>
{% endfor %}
</ul>
'''

# finds all pages of given tag
class PlistExtension(Extension):
    def on_generation_start(self, generator, config, all_files):
        # Get all tags
        if 'ex_tags' not in config:
            raise Exception("ERROR: Extension tags should be added before plist extension")

        for tag in config['ex_tags']['tags']:
            tmp = template_meta.replace('!###!TAGS!###!', str([tag["tag"]]))
            tmp = tmp.replace('!###!TITLE!###!', tag['label'])
            tmp = tmp.replace('!###!ROUTE!###!', f'~~BASE_URL~~/{tag["tag"]}')
            tmp = yaml.load(tmp, Loader=yaml.Loader)

            all_files.append({
                'filename': f'ex_tags_{tag["tag"]}.ex_tags.md',
                'content': template_content,
                'meta': tmp
            })
 
        # TODO: dolny limit liczby stron w danym tagu
        # TODO: kombinacje tagów i liczby stron
        # TODO: sortowanie stron po dacie (moze na front-endzie?)
        # for tag in config['ex_tags']['tags']:
        #     tag['pages'] = self.get_pages_with_all_tags(tag, generator, config)


    def preprocessing(self, generator, config, all_files):
        for file in all_files:
            if 'plist_tags' in file['meta']:
                target_tags = file['meta']['plist_tags']
                file['meta']['plist_pages'] = self.get_pages_with_all_tags(config, target_tags, all_files)


    def get_pages_with_all_tags(self, config, target_tags, all_files):
        #pages = config['ex_tags']['pages']
        res = []
        for page in all_files:
            if 'tags' in page['meta'] and set(target_tags).issubset(set(page['meta']['tags'])):
                res.append(page)
        return res

