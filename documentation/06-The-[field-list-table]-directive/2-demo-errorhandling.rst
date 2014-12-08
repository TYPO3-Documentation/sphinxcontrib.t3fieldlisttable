=======================================================
 2-demo-errorhandling.rst: Directive 'field-list-table'
=======================================================

---------------------------------------------
Checking and demonstrating error handling
---------------------------------------------

:author:    Martin Bless
:date:      2011-12-06
:email:     martin.bless@gmail.com
:web:       http://mbless.de
:copyleft:  This document has been placed into the public domain
:abstract:  Negative examples: What you can do to produce
            errors and how they are being handled.

.. sectnum::
.. contents::

About
=====
This document shows what you can do wrong and shows how these
errors are handled by the 'field-list-table' directive. Should
be turned into a real unittest later.

Tests
=====

.. ==================================================
   Missing content
   ==================================================
.. field-list-table::


.. ==================================================
   More than one item
   ==================================================
.. field-list-table::

   Hello!

   - bullet list item


.. ==================================================
   Wrong item
   ==================================================
.. field-list-table::

   Hello!

.. ==================================================
   Colspan not allowed in definition row.
   ==================================================
.. field-list-table::

 - :a..b:

.. ==================================================
   Rowspan not allowed in definition row.
   ==================================================
.. field-list-table::

 - :(abc:

.. ==================================================
   Duplicate field name in definition row
   ==================================================
.. field-list-table::

 - :abc:
   :abc:

.. ==================================================
   Illegal column width
   ==================================================
.. field-list-table::

 - :abc,z:

.. ==================================================
   Illegal column width
   ==================================================
.. field-list-table::

 - :abc,-1:

.. ==================================================
   Columns too wide
   ==================================================
.. field-list-table::

 - :abc,51:
   :bcd,51:

.. ==================================================
   Columns too wide
   ==================================================
.. field-list-table::
 :total-width: 1000

 - :abc,501:
   :bcd,501:

.. ==================================================
   Correct alignments
   ==================================================
.. field-list-table:: Correct alignment specifications

 - :a,,left top:     left top:     left   top
   :b,,l t:          l t:          left   top
   :c,,c m:          c m:          center middle
   :d,,r b:          r b:          right  bottom
   :e,,tO lEf:       tO lEf:       left   top
   :f,,mIdDl cEnTe:  mIdDl cEnTe:  center middle
   :g,,bOtTo rIgH:   bOtTo rIgH:   right  bottom
   :h,,t c t c:      t c t c:      center top

.. ==================================================
   Wrong alignment
   ==================================================
.. field-list-table::

 - :abc,,x:

.. ==================================================
   Data rows: illegal field name
   ==================================================
.. field-list-table::

 - :a:
 - :(a:

.. ==================================================
   Data rows: unknown field name at beginning of range
   ==================================================
.. field-list-table::

 - :a:
   :b:
   :c:
 - :x..c:

.. ==================================================
   Data rows: unknown field name at end of range
   ==================================================
.. field-list-table::

 - :a:
   :b:
   :c:
 - :a..x:

.. ==================================================
   Data rows: wrong order of fields in range
   ==================================================
.. field-list-table::

 - :a:
   :b:
   :c:
 - :c..a:

.. ==================================================
   Data rows: cell(s) specified more than once
   ==================================================
.. field-list-table::

 - :a:
   :b:
 - :a:
   :a:

.. ==================================================
   Data rows: cell(s) specified more than once
   ==================================================
.. field-list-table::

 - :a:
   :b:
   :c:
 - :a..c:
   :a:

.. ==================================================
   Data rows: cell(s) specified more than once
   ==================================================
.. field-list-table::

 - :a:
   :b:
   :c:
 - :a..c:
   :b:

.. ==================================================
   Data rows: cell(s) specified more than once
   ==================================================
.. field-list-table::

 - :a:
   :b:
   :c:
 - :a..c:
   :c:

.. ==================================================
   Data rows: cell(s) specified more than once
   ==================================================
.. field-list-table::

 - :a:
   :b:
   :c:
 - :a:
   :a..c:

.. ==================================================
   Data rows: cell(s) specified more than once
   ==================================================
.. field-list-table::

 - :a:
   :b:
   :c:
 - :b:
   :a..c:

.. ==================================================
   Data rows: cell(s) specified more than once
   ==================================================
.. field-list-table::

 - :a:
   :b:
   :c:
 - :c:
   :a..c:

.. ==================================================
   Data rows: rowspan cells must not have data
   ==================================================
.. field-list-table::

 - :a:
 - :a:
 - :(a): A

.. ==================================================
   Data rows: mismatch with previous row
   ==================================================
.. field-list-table::

 - :a:
   :b:
   :c:

 - :a:
   :b:
   :c:

 - :(a..c):

.. ==================================================
   xxx
   ==================================================
.. field-list-table::

 - :a:
   :b:
   :c:

 - :a..c:

 - :(a):

.. ==================================================
   xxx
   ==================================================
.. field-list-table::

 - :a:
   :b:
   :c:

 - :a..b:

 - :(b):

.. ==================================================
   xxx
   ==================================================
.. field-list-table::

 - :a:
   :b:
   :c:

 - :a..b:

 - :(b..c):


.. ==================================================
   xxx
   ==================================================
.. field-list-table::

 - :a:
   :b:
   :c:

 - :a..c:

 - :(a..b):

 - :(a..b):


.. ==================================================
   xxx
   ==================================================
.. field-list-table::
 :header-rows: 0
 :definition-row: 0

 - :a:

.. ==================================================
   xxx
   ==================================================
.. field-list-table::
 :header-rows: 1
 :definition-row: 0

 - :a:

.. ==================================================
   xxx
   ==================================================
.. field-list-table::
 :header-rows: 2
 :definition-row: 0

 - :a:

.. ==================================================
   xxx
   ==================================================
.. field-list-table::
 :header-rows: 0
 :definition-row: 1

 - :a:

.. ==================================================
   xxx
   ==================================================
.. field-list-table::
 :header-rows: 1
 :definition-row: 1

 - :a:

.. ==================================================
   xxx
   ==================================================
.. field-list-table::
 :header-rows: 2
 :definition-row: 1

 - :a:


.. ==================================================
   xxx
   ==================================================
.. field-list-table::
 :stub-columns: 1

 - :a:

.. ==================================================
   xxx
   ==================================================
.. field-list-table::
 :stub-columns: 2

 - :a:

