#! /usr/bin/python

# $Id$
# Author: Martin Bless <martin@mbless.de>
# Copyright: This module has been placed in the public domain.

"""
A minimal web front end to produce HTML
"""

from __future__ import absolute_import
from __future__ import print_function
if 1:
    import sys
    sys.argv = sys.argv[:1]
    sys.argv += ['--traceback']
    sys.argv += ['--source-link']
    sys.argv += ['--stylesheet-path=styles.css']
    sys.argv += ['2-demo-errorhandling.rst', '2-demo-errorhandling.rst.html']

print('Content-type:text/html')
print()
print('<pre>')
print("starting by importing 'rst2html_typo3'")
print("If no 'Finished.' follows here there probably has been an error.")


import rst2html_typo3

print()
print("Finished.")
print("Success is unknown.")
print("Please see if a new file has been produced.")
print('</pre>')
