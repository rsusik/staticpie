# DEPENDENCY: TAGS
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


template_meta = '''
route: !###!ROUTE!###!
template: tpl_only_body.html
extensions: [pagelist]
pagelist_tags: !###!TAGS!###!
title: !###!TITLE!###!
author: Robert
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
    <a href="{{page.meta.route}}">{{ page.meta.route }}</a>
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

        for tag in generator.config['tags']['tags']:
            tmp = template_meta.replace('!###!TAGS!###!', str([tag["tag"]]))
            tmp = tmp.replace('!###!TITLE!###!', tag['label'])
            tmp = tmp.replace('!###!ROUTE!###!', f'~~BASE_URL~~/{tag["tag"]}')
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

