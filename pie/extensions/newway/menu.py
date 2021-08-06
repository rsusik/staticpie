import numpy as np
from glob import glob
import yaml
from core.extension import Extension
from typing import List


from core.generator import (
    Generator, 
    ConfigType,
    FileStartType,
    FilePreType,
    FilePostType,
    FileEndType
)


class MenuExtension(Extension):
    
    def preprocessing(self, 
        generator : Generator, 
        config : ConfigType, 
        files : List[FilePreType]
    ):
        print('hello')
        

        return 0


