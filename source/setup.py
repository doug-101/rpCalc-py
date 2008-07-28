#!/usr/bin/env python
from distutils.core import setup
import py2exe

setup(name = 'rpcalc',
      windows = [{'script': 'rpcalc.py',
                  'icon_resources': [(1, 'rpcalc.ico')]}],
      options = {'py2exe': {'includes': ['sip'],
                            'dist_dir': 'dist/lib'}})

# run with: python setup.py py2exe
