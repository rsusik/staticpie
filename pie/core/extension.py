from typing import List
from .generator import (
    Generator, 
    ConfigType,
    FileStartType,
    FilePreType,
    FilePostType,
    FileEndType
)


class Extension:
    '''
    Implements any additional activities
    such as preprocessing and postprocessing of website.
    '''
    # def __init__(self):
    #     pass

    def preprocessing(self, 
        generator : Generator,
        files : List[FilePreType]
    ) -> None:
        '''
        Performs preprocessing of website
        i.e. may deliver additional data to template.

        Parameters:
        * generator - the generator that executes this function,
        * files - list of files (dictionary).
        '''
        
        pass

    def postprocessing(self, 
        generator : Generator,
        files : List[FilePostType]
    ) -> None:
        '''
        Performs postprocessing of website
        i.e. may remove bad words from output website.

        Parameters:
        * generator - the generator that executes this function,
        * files - list of files (dictionary), the content is html.
        '''

        pass

    def on_generation_start(self, 
        generator : Generator,
        files : List[FileStartType]
    ) -> None:
        '''
        Performs activities before markdown parser is executed.
        It can generate some additional templates/websites/markdowns.

        Paramters:
        * generator - the generator that executes this function,
        * files - list of files (dictionary).
        '''
        pass

    def on_generation_end(self, 
        generator : Generator,
        files : List[FileEndType]
    ) -> None:
        '''
        Performs activities after all html's are generated.
        It can read some stats, peform some additional activities
        on generated html files, clean directories, etc.

        Paramters:
        * generator - the generator that executes this function,
        * files - list of files (dictionary).
        '''
        
        pass