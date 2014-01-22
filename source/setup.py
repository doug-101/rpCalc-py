#!/usr/bin/env python3
from distutils.core import setup
import py2exe

setup(name = 'rpcalc',
      windows = [{'script': 'rpcalc.py',
                  'icon_resources': [(1, '../win/rpcalc.ico')]}],
      options = {'py2exe': {'includes': ['sip'],
                            'dist_dir': 'dist/lib'}})

# run with: python setup.py py2exe
