#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Author: Mathias Hauser
#Date: 

import os
from os import path


class post_cls(object):
    """handling of file names in the 'post' folder"""
    def __init__(self, folder_post, casedef, hist, modname, add_hist=True):
        super(post_cls, self).__init__()

        self.folder_post = folder_post
        self.casedef = casedef
        self._name = casedef['name']
        self._hist = hist
        self._modname = modname
        self.add_hist = add_hist
        

    def pre_suf(self, prefix='', suffix='', prefix_folder=False, 
                file_type='nc'):
        """
        Create filename by attaching pre- and suffix to std name
        """

        sep = '.'

        # empty list if no prefix is given
        prefix = prefix if prefix != '' else []
        suffix = suffix if suffix != '' else []

        # check if prefix/ suffix is 
        if isinstance(prefix, basestring):
            prefix = [prefix]

        if isinstance(suffix, basestring):
            suffix = [suffix]

        file_base = [self._name,     # name of run
                     self._modname,  # name of module
                    ]

        if self.add_hist:
            file_base += [self._hist]      # hist file name

        file = sep.join(prefix + file_base + suffix + [file_type])

        if prefix_folder:
            folder = os.path.join(self.folder_post, *prefix)
            _mkdir(folder)
        else:
            folder = self.folder_post
    

        return os.path.join(folder, file)


def _mkdir(directory):
    # create a directory
    try:
        os.makedirs(directory)   
    except OSError as e:
        pass



    def full(self, name, file_type='nc'):
        """
        Create filename
        """
        sep = '.'
        
        file = sep.join([name, file_type])
        
        return path.join(self.folder_post, file)