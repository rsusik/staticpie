import numpy as np
from glob import glob
import yaml
from core.extension import Extension
import shutil, os

template = '''
---
route: !###!ROUTE!###!
template: tpl_only_body.html
extensions: [plist.py]
plist_tags: !###!TAGS!###!
title: !###!TITLE!###!
author: Robert
---

You are at {{ route }}

Articles:
<ul>
{% for page in plist_pages %}
    <li>
    {{ page.filename }} <br />
    {{ page.title }} <br />
    {{ page.author }} <br />
    {{ page.date }} <br />
    {{ page.summary }} <br />
    <a href="{{page.route}}">{{ page.route }}</a>
    </li>
{% endfor %}
</ul>
'''

# finds all pages of given tag
class PlistExtension(Extension):
    def on_generation_start(self, generator, config):
        # Get all tags
        if 'all_tags' not in config:
            raise Exception("ERROR: Extension tags should be added before plist extension")
        os.makedirs( f'{config["ROOT_FOLDER"]}/+plist_pages', exist_ok=True )

        for tag in config['all_tags']:
            with open(f'{config["ROOT_FOLDER"]}/+plist_pages/{tag["tag"]}.md', 'wt') as f:
                tmp = template.replace('!###!TAGS!###!', str([tag["tag"]]))
                tmp = tmp.replace('!###!TITLE!###!', tag['label'])
                tmp = tmp.replace('!###!ROUTE!###!', f'~~BASE_URL~~/{tag["tag"]}')
                f.write(tmp)
        # TODO: dolny limit liczby stron w danym tagu
        # TODO: kombinacje tagów i liczby stron
        # TODO: sortowanie stron po dacie (moze na front-endzie?)
        

    def preprocessing(self, generator, config, webconf, md_code):
        pages = []
        
        if 'plist_tags' not in webconf:
            return md_code
            #raise Exception(f'ERROR: plist_tags not defined in page configuration.{webconf}')
        target_tags = webconf['plist_tags']
        for filename in generator.get_md_files():
            tmp_md_code, tmp_md_conf = generator.read_markdown_file(filename)
            conf = yaml.load(tmp_md_conf, Loader=yaml.Loader)
            if 'tags' in conf:
                for tag in conf['tags']:
                    if tag in target_tags:
                        tmp_page_conf = {
                            key:generator.inject_constants(config, value) if isinstance(value, str) else value 
                            for key, value in yaml.load(tmp_md_conf, Loader=yaml.Loader).items()
                        }
                        pages.append({
                            'filename': filename,
                            'title': tmp_page_conf['title'],
                            'date': tmp_page_conf['date'] if 'date' in tmp_page_conf else None,
                            'summary': tmp_page_conf['summary'] if 'summary' in tmp_page_conf else '',
                            'route': tmp_page_conf['route'],
                            'author': tmp_page_conf['author'] if 'author' in tmp_page_conf else ''
                        })
                        break
        config['plist_pages'] = pages

        return md_code

