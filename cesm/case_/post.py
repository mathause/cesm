#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Author: Mathias Hauser
#Date: 


from os import path


class post_cls(object):
    """handling of file names in the 'post' folder"""
    def __init__(self, folder_post, casedef, hist, modname):
        super(post_cls, self).__init__()

        self.folder_post = folder_post
        self.casedef = casedef
        self._name = casedef['name']
        self._hist = hist
        self._modname = modname
        

    def pre_suf(self, prefix='', suffix='', file_type='nc'):
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
                     self._hist      # hist file name
                    ]


        file = sep.join(prefix + file_base + suffix + [file_type])


        return path.join(self.folder_post, file)


    def full(self, name, file_type='nc'):
        """
        Create filename
        """
        sep = '.'
        
        file = sep.join([name, file_type])
        
        return path.join(self.folder_post, file)