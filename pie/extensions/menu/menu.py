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


class MenuExtension(Extension):
    def preprocessing(self, 
        generator : Generator,
        files : List[FilePreType]
    ):
        menu_items = []
        
        for file in files:
            if 'menu' in file['meta']:
                menu_item = file['meta']['menu'].copy()
                self._default_if_null(menu_item, 'order', 999)
                menu_item['route'] = file['meta']['route']
                menu_items.append(menu_item)

        generator.config["menu"] = sorted(
            [self._get_children(item, menu_items) for item in menu_items if 'parent' not in item or item["parent"] is None],
            key=lambda el: el['order']
        )

        return 0


    def _get_children(self, el, menu_items):
        if 'id' not in el or el["id"] is None:
            return el
        children = sorted(
            [item for item in menu_items if 'parent' in item and item["parent"] == el["id"] ],
            key=lambda el: el['order']
        )
        el["children"] = children

        for child in children:
            child = self._get_children(child, menu_items)
        return el


    def _default_if_null(self, el, key, default):
        if key not in el:
            el[key] = default

