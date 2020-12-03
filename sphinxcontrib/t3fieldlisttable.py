#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Martin Bless <martin@mbless.de>
# Credits: David Goodger <goodger@python.org>; David Priest

# BSD style license:

# Copyright (c) 2011, Martin Bless <martin@mbless.de>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



"""
Directive for field-list-table elements.
"""

from __future__ import absolute_import
from six.moves import range
__docformat__ = 'reStructuredText'

import sys

from docutils.utils import SystemMessagePropagation
from docutils.parsers.rst import directives
from docutils import nodes
from docutils.parsers.rst.directives.tables import Table
from docutils import DataError

COMMENT_DRAWING_CHARS = '-=_~.*`\'"+'

class FieldListTableError(DataError):
    pass

def yes_no_zero_one(argument):
    return directives.choice(argument, ('yes', 'no', '0', '1'))

class FieldListTable(Table):

    """
    Implement tables whose data is encoded as a two-level list. The outer
    level is a bullet list. Each list items make up a table row. The contents
    of each list item is a field list where field names are used to determine
    the table columns. For the original idea see
    http://docutils.sf.net/docs/dev/rst/alternatives.html#list-driven-tables
    """

    option_spec = {
        'class'          : directives.class_option,
        'name'           : directives.unchanged,
        'allow-comments' : yes_no_zero_one,
        'definition-row' : yes_no_zero_one,
        'header-rows'    : directives.nonnegative_int,
        'stub-columns'   : directives.nonnegative_int,
        'total-width'    : directives.nonnegative_int,
        'debug-cellinfo' : yes_no_zero_one,
        'transformation' : yes_no_zero_one,
    }


    def run(self):
        self.errorstr = None
        self.cropped = None
        self.colNum = None
        self.rowNum = None
        self.columnIds = []
        self.columnIdsIndexes = {}
        self.tableData = []
        self.tableInfo = []
        try:
            result = self.run2()
        except FieldListTableError as errorargs:
            self.errorstr = str(errorargs)
        if not self.errorstr is None:
            error = self.errormsg(self.errorstr)
            result = [error]
        return result


    def run2(self):
        if not self.content:
            msg = 'The directive is empty - content is required.'
            raise FieldListTableError(msg)
        title, messages = self.make_title()
        self.node = nodes.Element()
        self.state.nested_parse(self.content, self.content_offset, self.node)
        field_list_table_off = False
        if hasattr(self.state_machine.document.settings,
                   'field_list_table_off'):
            field_list_table_off = \
                self.state_machine.document.settings.field_list_table_off
        if self.options.get('transformation') in ['no', '0']:
            field_list_table_off = True
        if field_list_table_off:
            # transformation has been turned off by cmd line option
            # --field-list-table-off or by directive option
            # :transformation: no
            # So we skip the transformation process
            return self.node.children
        if len(self.node) != 1:
            msg =("Exactly one item (a bullet list) expected. "
                  "%s items found instead." % len(self.node))
            raise FieldListTableError(msg)
        if not isinstance(self.node[0],nodes.bullet_list):
            msg = ("Content type is wrong. Exactly one bullet list "
                   "is expected.")
            raise FieldListTableError(msg)
        if self.options.get('definition-row') in ['yes', '1']:
            self.definitionRow = 1
        else:
            self.definitionRow = 0
        bulletList = self.node[0]
        self.checkBulletList(bulletList)
        if self.options.get('allow-comments', True):
            self.node[0] = self.removeComments(bulletList=self.node[0])
        bulletList = self.node[0]
        self.processDefinitionRow(listItem=bulletList[0])
        self.adjustColumnWidths()
        self.checkAlignments()
        self.checkMoreAttributes()
        bulletList = self.node[0]
        self.processDataRows(bulletList)
        # go and process our data rows':
        headerRows = self.options.get('header-rows', 0)
        stubColumns = self.options.get('stub-columns', 0)
        self.checkTableDimensions(self.tableData, headerRows, stubColumns)
        self.checkRowspans()
        tableNode = self.buildTableFromFieldList(headerRows, stubColumns)
        tableNode['classes'] += self.options.get('class', [])
        self.add_name(tableNode)
        if title:
            tableNode.insert(0, title)
        return [tableNode] + messages

    def crop(self, text, maxlines=10, maxlen=800, moretext='\n[...]'):
        lines = text[:maxlen].split('\n',maxlines)
        addmoretext = (len(text) > maxlen or (len(lines) >
                                              maxlines and lines[maxlines]))
        while lines and not lines[-1].strip():
            del lines[-1]
        if addmoretext:
            lines.extend(moretext.split('\n'))
        return '\n'.join(lines)

    def errormsg(self, msg):
        if self.cropped is None:
            self.cropped = self.crop(self.block_text, 10, 800, '\n[...]')
        sourceinfo = nodes.container('')
        lines = []
        if not self.colNum is None:
            lines.append('colNum: %s' % self.colNum)
        if not self.rowNum is None:
            lines.append('rowNum: %s' % self.rowNum)
        if lines:
            lines = ['Processing:', '' ] + lines
            sourceinfo += nodes.literal_block('', '\n'.join(lines))
        sourceinfo += nodes.literal_block(self.cropped, self.cropped)
        error = self.state_machine.reporter.error(
            'Error in directive "%s": %s' % (self.name, msg),
            sourceinfo, line=self.lineno)
        return error

    def removeComments(self, bulletList):
        newBulletList = nodes.bullet_list()
        for bulletListItem in bulletList:
            newFieldList = nodes.field_list()
            fieldList = bulletListItem[0]
            for field in fieldList:
                fieldName = field[0]
                fieldNameAsText = fieldName.astext()
                firstChar = fieldNameAsText[0]
                if firstChar in COMMENT_DRAWING_CHARS:
                    if (firstChar * len(fieldNameAsText)) == fieldNameAsText:
                        pass
                    else:
                        newFieldList += field
                else:
                    newFieldList += field
            if len(newFieldList):
                newListItem = nodes.list_item()
                newListItem += newFieldList
                newBulletList += newListItem
        return newBulletList

    def processDefinitionRow(self, listItem):
        dataRow = []
        infoRow = []
        lenOfListItem = len(listItem)
        fieldList = listItem[0]
        self.rowNum = 0
        for self.colNum, field in enumerate(fieldList):
            fieldName = field[0]
            fieldBody = field[1]
            fieldNameRaw = fieldName.astext()
            columnIdRaw,colwidth,align,more = self.getPartsOfFieldname(
                fieldNameRaw, isDefinitionRow=True)
            # in case of definition row:
            #    columnIdRaw = columnIdRange = columnId
            columnIdRange = columnIdRaw
            columnId = columnIdRaw
            if '..' in columnId:
                msg = ("colspan ('%s') is not allowed in the first row "
                       "as this is the definition row." % columnId)
                raise FieldListTableError(msg)
            if columnId.startswith('('):
                msg = ("rowspan ('%s') is not allowed in the first row "
                       "as this is the definition row." % columnId)
                raise FieldListTableError(msg)
            if self.columnIdsIndexes.get(columnId, None) != None:
                msg = "Duplicate column '%s'." % columnId
                raise FieldListTableError(msg)
            cellInfo = {}
            cellInfo['columnId'     ] = columnId
            cellInfo['columnIdRange'] = columnIdRange
            cellInfo['columnIdRaw'  ] = columnIdRaw
            cellInfo['fieldNameRaw' ] = fieldNameRaw
            cellInfo['align'        ] = align
            cellInfo['more'         ] = more
            cellInfo['colspan'      ] = 1
            cellInfo['rowspan'      ] = 1
            cellInfo['colNum'       ] = self.colNum
            cellInfo['rowNum'       ] = self.rowNum
            cellInfo['colwidth'     ] = colwidth

            self.columnIds.append(columnId)
            self.columnIdsIndexes[columnId] = self.colNum

            infoRow.append(cellInfo)
            dataRow.append(fieldBody.children)

        self.tableInfo.append(infoRow)
        self.tableData.append(dataRow)


    def processDataRows(self,bulletList):
        for rowNum in range(1, len(bulletList)):
            bulletListItem = bulletList[rowNum]
            fieldList = bulletListItem[0]
            dataRow = []
            for cell in self.columnIds:
                dataRow.append(None)
            infoRow = []
            for cell in self.columnIds:
                infoRow.append({})
            for fieldNum, field in enumerate(fieldList):
                fieldName = field[0]
                fieldNameRaw = fieldName.astext()
                (columnIdRaw, colwidth, align, more) = \
                    self.getPartsOfFieldname(fieldNameRaw)
                rowspanSituation = False
                if columnIdRaw.startswith('('):
                    if not columnIdRaw.endswith(')'):
                        msg = "Illegal field name '%s'." % fieldNameRaw
                        raise FieldListTableError(msg)
                    rowspanSituation = True
                    columnIdRange = columnIdRaw[1:-1]
                else:
                    columnIdRange = columnIdRaw

                colspan_situation = '..' in columnIdRange
                if colspan_situation:
                    columnId, endId = columnIdRange.split('..', 1)
                    startIdIndex = self.columnIdsIndexes.get(columnId, None)
                    endIdIndex = self.columnIdsIndexes.get(endId, None)
                else:
                    columnId = columnIdRange
                    endId    = columnIdRange
                    startIdIndex = self.columnIdsIndexes.get(columnId, None)
                    endIdIndex = startIdIndex
                if startIdIndex is None:
                    msg = ("Field '%s' of range '%s' does not exist."
                           % (columnId, columnIdRange))
                    raise FieldListTableError(msg)
                if endIdIndex is None:
                    msg = ("Field '%s' of range '%s' does not exist."
                           % (endId, columnIdRange))
                    raise FieldListTableError(msg)
                if endIdIndex < startIdIndex:
                    msg = ("Field names '%s' and '%s' in range '%s' have "
                           "wrong order." % (columnId, endId, columnIdRange))
                    raise FieldListTableError(msg)
                # check and prepare what has been given as alignment spec
                if align:
                    dummy, hAlign, vAlign = self.isValidAlignment(align)
                else:
                    hAlign = []
                    vAlign = []
                colAlign = self.tableInfo[0][startIdIndex].get('align', None)
                if colAlign:
                    dummy, colHAlign, colVAlign = self.isValidAlignment(
                        colAlign)
                else:
                    colHAlign = []
                    colVAlign = []
                align = ' ' .join((hAlign or colHAlign) +
                                  (vAlign or colVAlign))
                for self.colNum in range(startIdIndex, endIdIndex + 1):
                    if not dataRow[self.colNum] is None:
                        msg = ("Value for column %s ('%s') is specified "
                               "more than once." % (self.colNum + 1,
                            self.tableInfo[0][self.colNum]['columnId']))
                        raise FieldListTableError(msg)
                if infoRow[startIdIndex].get('isInColspan',None):
                    msg = ("Value for table column %s ('%s') is specified "
                           "more than once." % (startIdIndex + 1,
                            self.tableInfo[0][startIdIndex]['columnId']))
                    raise FieldListTableError(msg)
                infoRow[startIdIndex]['colNum'        ] = startIdIndex
                infoRow[startIdIndex]['rowNum'        ] = rowNum
                infoRow[startIdIndex]['columnId'      ] = columnId
                infoRow[startIdIndex]['columnIdRange' ] = columnIdRange
                infoRow[startIdIndex]['columnIdRaw'   ] = columnIdRaw
                infoRow[startIdIndex]['fieldNameRaw'  ] = fieldNameRaw
                if align:
                    infoRow[startIdIndex]['align'] = align
                fieldBody = field[1]
                if rowspanSituation:
                    if fieldBody.children:
                        msg = ("No content is allowed for cells that are "
                               "covered by a rowspan.")
                        raise FieldListTableError(msg)
                    infoRow[startIdIndex]['isFollowingRow'] = True
                    rowspanSituation = False
                else:
                    dataRow[startIdIndex] = fieldBody.children
                colspan = endIdIndex - startIdIndex
                if colspan:
                    infoRow[startIdIndex]['colspan'] = colspan + 1
                    for i in range(startIdIndex + 1 , endIdIndex + 1):
                        infoRow[i]['colNum'] = i
                        infoRow[i]['rowNum'] = rowNum
                        infoRow[i]['isInColspan'] = True
            self.tableInfo.append(infoRow)
            self.tableData.append(dataRow)

    def adjustColumnWidths(self):
        resultRow = []
        sumOfWidths = 0
        rowWidth = self.options.get('total-width', 100)
        if 'pass 1':
            cntMissingOnes = 0
            infoRow = self.tableInfo[0]
            for info in infoRow:
                colwidth = info['colwidth']
                if colwidth is None or colwidth == '':
                    cntMissingOnes += 1
                else:
                    valueError = False
                    try:
                        colwidth = int(colwidth)
                    except ValueError:
                        valueError = True
                    if valueError or colwidth < 0:
                        msg = ("Illegal column width '%s'. Must be integer "
                               "between 0 and %s." % (colwidth, rowWidth))
                        raise FieldListTableError(msg)
                    sumOfWidths += colwidth
                resultRow.append(colwidth)

            if sumOfWidths > rowWidth:
                msg = ("The columns have a total width of %s. This "
                       "exceeds the allowed maximum of %s." %
                       (sumOfWidths, rowWidth))
                raise FieldListTableError(msg)
        if 'pass 2':
            nToGo = cntMissingOnes
            widthInserted = 0
            for i, colwidth in enumerate(resultRow):
                if colwidth in [None, '']:
                    if nToGo == 1:
                        # avoid rounding artefacts
                        widthToInsert = rowWidth - sumOfWidths - widthInserted
                    else:
                        widthToInsert = int((rowWidth - sumOfWidths) /
                                            cntMissingOnes)
                    resultRow[i] = widthToInsert
                    widthInserted += widthToInsert
                    nToGo = nToGo - 1
                infoRow[i]['colwidth'] = resultRow[i]

    def checkAlignments(self):
        # see http://www.loc.gov/ead/tglib/att_tab.html
        # for ideas about naming alignments
        infoRow = self.tableInfo[0]
        for i,info in enumerate(infoRow):
            v = info['align']
            if v:
                canonical, hAlign, vAlign = self.isValidAlignment(v)
                if not canonical:
                    msg = "Unknown alignment '%s'" % v
                    raise FieldListTableError(msg)
                else:
                    v = canonical

    def isValidAlignment(self, v):
        hAlign = []
        vAlign = []
        for part in v.split(' '):
            partLower = part.lower()
            valid = False
            for canonical in ['left', 'right', 'center', 'justify']:
                if canonical.startswith(partLower):
                    valid = True
                    if not canonical in hAlign:
                        hAlign.append(canonical)
                    break
            if not valid:
                for canonical in ['top', 'bottom', 'middle']:
                    if canonical.startswith(partLower):
                        valid = True
                        if not canonical in vAlign:
                            vAlign.append(canonical)
                        break
        if not valid or len(hAlign)>1 or len(vAlign)>1:
            canonical = False
        else:
            canonical = ' '.join(hAlign + vAlign)
        return canonical, hAlign, vAlign

    def getPartsOfFieldname(self, fieldNameRaw, isDefinitionRow=False):
        parts = fieldNameRaw.split(',')
        lenParts = len(parts)
        columnIdRaw = parts[0].strip()
        colwidth = None
        align = None
        more = None
        if lenParts > 1:
            colwidth = parts[1].strip()
            if lenParts > 2:
                align = parts[2].strip()
                if lenParts > 3:
                    more = parts[3:]
        if colwidth:
            if not isDefinitionRow:
                msg = ("Column width specification is only allowed in "
                       "the definition row (first row).")
                raise FieldListTableError(msg)
        else:
            colwidth = None
        if align:
            canonical, hAlign, vAlign = self.isValidAlignment(align)
            if not canonical:
                msg = "Unknown alignment '%s'." % align
                raise FieldListTableError(msg)
            else:
                align = canonical
        else:
            align = None
        if not more:
            more = None
        result = (columnIdRaw, colwidth, align, more)
        return result

    def checkMoreAttributes(self):
        pass

    def checkBulletList(self, bulletList):
        for self.rowNum, listItem in enumerate(bulletList):
            listLen = len(listItem)
            if not listLen == 1:
                msg = ("Exactly one item (a field list) for bullet list "
                       "item expected. %s items found instead." % listLen)
                raise FieldListTableError(msg)
            if not isinstance(listItem[0], nodes.field_list):
                msg = ("Exactly on field list as bullet list item "
                       "expected.")
                raise FieldListTableError(msg)

    def checkTableDimensions(self, rows, header_rows, stub_columns):
        if (len(rows)-self.definitionRow) < header_rows:
            if self.definitionRow:
                msg = "1 definition row and "
            else:
                msg = ''
            msg += ("%s header row(s) specified but only %s row(s) "
                   "supplied." % (header_rows, len(rows)))
            raise FieldListTableError(msg)
        if (len(rows)-self.definitionRow) == header_rows:
            if self.definitionRow:
                msg = "1 definition row and "
            else:
                msg = ''
            msg += ("%s header row(s) specified but only %s row(s) "
                   "supplied. There's no data remaining for the table body."
                    % (header_rows, len(rows)))
            raise FieldListTableError(msg)
        for row in rows:
            if len(row) < stub_columns:
                msg = ("%s stub column(s) specified but only %s column(s) "
                       "supplied." % (stub_columns, len(row)))
                raise FieldListTableError(msg)
            if len(row) == stub_columns > 0:
                msg = ("%s stub column(s) specified but only %s column(s) "
                       "supplied. There is no data remaining for the "
                       "table body."
                       % (stub_columns, len(row)))
                raise FieldListTableError(msg)

    def checkRowspans(self):
        headerRows = self.options.get('header-rows', 0)
        firstTBodyRow = headerRows + self.definitionRow
        for info in self.tableInfo[0]:
            if info.get('isFollowingRow'):
                msg = ("The first table row is the definition row. It cannot "
                       "have cells that belong to a previous rowspan.")
                raise FieldListTableError(msg)
        for info in self.tableInfo[firstTBodyRow]:
            if info.get('isFollowingRow', False):
                msg = ("The first table body row cannot have cells that "
                       "belong to a previous rowspan.")
                raise FieldListTableError(msg)
        for self.rowNum in range(len(self.tableData)-1,
                                 self.definitionRow-1,
                                 -1):
            infoRow = self.tableInfo[self.rowNum]
            for self.colNum, info in enumerate(infoRow):
                if info.get('isFollowingRow'):
                    rowspan = 1
                    found = False
                    for rowNum2 in range(self.rowNum - 1,
                                         self.definitionRow-1,
                                         -1):
                        rowspan += 1
                        info2 = self.tableInfo[rowNum2][self.colNum]
                        if info2.get('isInColspan'):
                            msg = ("rowspan '%s' does not match previous "
                                   "row. Found a colspan instead." %
                                   (info['columnIdRange'],))
                            raise FieldListTableError(msg)
                        val2 = info2.get('columnIdRange', None)
                        val1 = info.get('columnIdRange', None)
                        if val2  != val1 :
                            msg = ("rowspan '%s' does not match previous "
                                   "field '%s'" % (val1, val2))
                            raise FieldListTableError(msg)
                        if not info2.get('isFollowingRow'):
                            if info2.get('rowspan', None) is None:
                                info2['rowspan'] = rowspan
                            found = True
                        if found:
                            break

    def buildTableFromFieldList(self, headerRows, stubColumns):
        table = nodes.table()
        tgroup = nodes.tgroup(cols=len(self.tableInfo[0]))
        table += tgroup
        for info in self.tableInfo[0]:
            colwidth = info['colwidth']
            colspec = nodes.colspec(colwidth=colwidth)
            if stubColumns:
                colspec.attributes['stub'] = 1
                stubColumns = stubColumns - 1
            if not info['align'] is None:
                colspec.attributes['align'] = info['align']
            if not info['more'] is None:
                colspec.attributes['more'] = info['more']
            tgroup += colspec
        rows = []
        for self.rowNum, row in enumerate(self.tableData):
            if self.definitionRow and self.rowNum == 0:
                continue
            rowNode = nodes.row()
            for self.colNum, cell in enumerate(row):
                info = self.tableInfo[self.rowNum][self.colNum]
                if info.get('isInColspan'):
                    pass
                elif info.get('isFollowingRow'):
                    pass
                else:
                    entry = nodes.entry()
                    if self.options.get('debug-cellinfo') in ['yes','1']:
                        interesting = [
                            (1,'colNum'),
                            (1,'rowNum'),
                            (0,'colwidth'),
                            (0,'columnId'),
                            (0,'align'),
                            (0,'more'),
                            (1,'colspan'),
                            (1,'rowspan'),
                            (1,'columnIdRange'),
                            (1,'columnIdRaw'),
                            (1,'fieldNameRaw')]
                        debugLines = []
                        for flag,k in interesting:
                            if flag:
                                debugLines.append('| %s=%s \n' %
                                                  (k, info.get(k)))
                        if debugLines:
                            p = nodes.paragraph('', ''.join(debugLines))
                            entry += p
                    entry += cell
                    info = self.tableInfo[self.rowNum][self.colNum]
                    morecols = info.get('colspan',1) - 1
                    if morecols:
                        entry.attributes['morecols'] = morecols
                    morerows = info.get('rowspan', 1) - 1
                    if morerows:
                        entry.attributes['morerows'] = morerows
                    align = info.get('align')
                    if align:
                        entry.attributes['align'] = align
                    more = info.get('more')
                    if more:
                        entry.attributes['more'] = more
                    rowNode += entry
            rows.append(rowNode)
        if headerRows:
            thead = nodes.thead()
            thead.extend(rows[:headerRows])
            tgroup += thead
        tbody = nodes.tbody()
        tbody.extend(rows[headerRows:])
        tgroup += tbody
        return table


def setup(app):
    app.add_directive('t3-field-list-table', FieldListTable)
    return {
        "version": "0.3.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

