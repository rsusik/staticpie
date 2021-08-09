# DEPENDENCY: TAGS
import os
import yaml
from typing import List

from pie.core.extension import Extension
from pie.core.generator import (
    Generator, 
    ConfigType,
    FileStartType,
    FilePreType,
    FilePostType,
    FileEndType
)
from pie.core.utils import *


template_meta = '''
route: !###!ROUTE!###!
template: !###!PAGELIST_DEFAULT_TEMPLATE!###!
extensions: [pagelist]
pagelist_tags: !###!TAGS!###!
title: !###!TITLE!###!
author: Generated
'''

template_content = '''
You are at {{ route }}

Articles:

{{pagelist_pages}}

<ul>
{% for page in meta.pagelist_pages %}
    <li>
    {{ page.filename }} <br />
    {{ page.meta.title }} <br />
    {{ page.meta.author }} <br />
    {{ page.meta.date }} <br />
    {{ page.meta.summary }} <br />
    <a href="{{config['PROTOCOL']}}{{page.meta.route}}">{{ page.meta.route }}</a>
    </li>
{% endfor %}
</ul>
'''

# finds all pages of given tag
class PagelistExtension(Extension):
    def on_generation_start(self, 
        generator : Generator,
        files : List[FileStartType]
    ) -> None:
        # Get all tags
        if 'tags' not in generator.config:
            raise Exception("ERROR: Extension tags should be added before pagelist extension")

        if 'pagelist' not in generator.config:
            generator.config['pagelist'] = {}

        if 'template' not in generator.config['pagelist']:
            log.debug(generator.config['ROOT_FOLDER'])
            template_path = generator.config['ROOT_FOLDER'] + '/' + 'pagelist_default_template.html'
            if not os.path.isfile(template_path):
                with open(template_path, 'wt') as f:
                    f.write(template_content)
            generator.config['pagelist']['template'] = 'pagelist_default_template.html'

        for tag in generator.config['tags']['tags']:
            tmp = template_meta.replace('!###!TAGS!###!', str([tag["tag"]]))
            tmp = tmp.replace('!###!TITLE!###!', tag['label'])
            tmp = tmp.replace('!###!ROUTE!###!', f'~~BASE_URL~~/{tag["tag"]}')
            tmp = tmp.replace('!###!PAGELIST_DEFAULT_TEMPLATE!###!', f"{generator.config['pagelist']['template']}")
            tmp = yaml.load(tmp, Loader=yaml.Loader)

            files.append({
                'filename': f'tags_{tag["tag"]}.tags.md',
                'content': template_content,
                'meta': tmp
            })


    def preprocessing(self, 
        generator : Generator,
        files : List[FilePreType]
    ) -> None:
        for file in files:
            if 'pagelist_tags' in file['meta']:
                target_tags = file['meta']['pagelist_tags']
                file['meta']['pagelist_pages'] = self.get_pages_with_all_tags(
                    target_tags, 
                    files
                )


    def get_pages_with_all_tags(
        self,
        target_tags : List, 
        files : List[FilePreType]
    ):
        res = []
        for page in files:
            if 'tags' in page['meta'] and set(target_tags).issubset(set(page['meta']['tags'])):
                res.append(page)
        return res

