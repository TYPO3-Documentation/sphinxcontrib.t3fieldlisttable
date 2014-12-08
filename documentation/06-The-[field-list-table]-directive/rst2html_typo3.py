#!d:\python27\python.exe

# Author: Martin Bless <martin.bless@gmail.com>
# Credits: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
A front end to the Docutils Publisher, producing HTML.

((extended functionality, TYPO3 ...))

"""

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass


import docutils.core
from docutils import nodes, SettingsSpec
from docutils.core import publish_cmdline, default_usage
from docutils.parsers.rst.directives import register_directive

extraDirectives = []

# additional directives:
from fieldlisttable import FieldListTable
register_directive('field-list-table', FieldListTable)
extraDirectives.append('field-list-table')


# augmented and modified writer
from docutils.writers.html4css1 import HTMLTranslator

class MyHTMLTranslator(HTMLTranslator):

    def visit_title(self, node):
        HTMLTranslator.visit_title(self, node)
        if isinstance(node.parent, nodes.Admonition):
            close_tag = self.context.pop()
            extra = '<div class="layout-admonition-icon"></div>\n'
            self.context.append(close_tag + extra)

    def visit_entry(self, node):
        atts = {}
        atts['class'] = []
        if isinstance(node.parent.parent, nodes.thead):
            atts['class'].append('head')
        if node.parent.parent.parent.stubs[node.parent.column]:
            # "stubs" list is an attribute of the tgroup element
            atts['class'].append('stub')
        if atts['class']:
            tagname = 'th'
        else:
            tagname = 'td'
        if 'align' in node:
            surprise = False
            for part in node['align'].split(' '):
                # what we expect
                if part in ['left', 'right', 'center',
                            'justify', 'top', 'bottom',
                            'middle']:
                    pass
                else:
                    surprise = True
            if 1 or not surprise:
                atts['class'].extend(node['align'].split(' '))
        if atts['class']:
            atts['class'] = ' '.join(atts['class'])
        else:
            del atts['class']
        node.parent.column += 1
        if 'morerows' in node:
            atts['rowspan'] = node['morerows'] + 1
        if 'morecols' in node:
            atts['colspan'] = node['morecols'] + 1
            node.parent.column += node['morecols']
        self.body.append(self.starttag(node, tagname, '', **atts))
        self.context.append('</%s>\n' % tagname.lower())
        if len(node) == 0:              # empty cell
            self.body.append('&nbsp;')
        self.set_first_last(node)

myWriter = docutils.writers.html4css1.Writer()
myWriter.translator_class = MyHTMLTranslator



# make description more precise
description = (
    'Generates (X)HTML documents from '
    'standalone reStructuredText '
    'sources. ' )
if extraDirectives:
    description += ('With extra directives: %s ' %
                    (', '.join(extraDirectives),))
description += docutils.core.default_description


# specify additional commandline options
from docutils import SettingsSpec
class MySettingsSpec(SettingsSpec):
    settings_spec = (
        'Options related to TYPO3 documentation',
        None,
        (('The field-list-table directive transforms nested lists '
          'into a table structure. If turned off with this options '
          'the transformation is omitted.',
          ['--field-list-table-off'],
          {'action': 'store_true','default':False}),
         ))
settings_spec = MySettingsSpec()


if 0 and 'developing':
    import sys
    if len(sys.argv) == 1:
        sys.argv = sys.argv[:1]
        # sys.argv += ['--help']
        sys.argv += ['--traceback']
        sys.argv += ['--stylesheet-path=styles.css']
        # sys.argv += ['--field-list-table-off']
        sys.argv += ['1-demo.rst', '1-demo.rst.html']

if 0:
    # This is the original form.
    publish_cmdline(writer_name='html', description=description)

if 0:
    # This is our extended version. It works but is very compact and
    # therefore hard to understand.
    publish_cmdline(writer=myWriter,
                    description=description,
                    settings_spec=settings_spec)

# We prefer the following 'long' code instead of the above compact one because
# its easier to understand and to tweak.

from docutils.core import Publisher
default_description = docutils.core.default_description
reader = None
reader_name = 'standalone'
parser = None
parser_name = 'restructuredtext'

if 0:
    writer = None
    writer_name = 'html'
else:
    writer = myWriter
    writer_name = None


settings = None
settings_spec = settings_spec
settings_overrides = None
config_section = None
enable_exit_status = 1
argv = None
usage = default_usage
description = default_description

pub = Publisher(reader, parser, writer, settings)
pub.set_components(reader_name, parser_name, writer_name)

if pub.settings is None:
    pub.process_command_line(
        argv,
        usage,
        description,
        settings_spec,
        config_section,
        **(settings_overrides or {}))

output = pub.publish(
    argv,
    usage,
    description,
    settings_spec,
    settings_overrides,
    config_section,
    enable_exit_status)
