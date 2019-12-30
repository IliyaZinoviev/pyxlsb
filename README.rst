pyxlsb
======

|PyPI| |Build Status|

``pyxlsb`` is an Excel 2007-2010 Binary Workbook (xlsb) parser for Python. The
library is currently very limited, but should be functional enough for basic
data extraction or conversion.

Install
-------

.. code:: bash

   pip install pyxlsb

Usage
-----

**WARNING**: Consult the README of the tag corresponding to the version you're
using, the usage may have changed since the last release.

The module exposes an ``open_workbook(name)`` method (similar to Xlrd and
OpenPyXl) for opening XLSB files. The Workbook object representing the file is
returned.

.. code:: python

   from pyxlsb import open_workbook
   with open_workbook('Book1.xlsb') as wb:
       # Do stuff with wb

The Workbook object exposes a ``get_sheet(idx)`` method for retrieving a
Worksheet instance.

.. code:: python

   # Using the sheet index (0-based, unlike VBA)
   with wb.get_sheet(0) as sheet:
       # Do stuff with sheet

   # Using the sheet name
   with wb.get_sheet('Sheet1') as sheet:
       # Do stuff with sheet

A ``sheets`` property containing the sheet names is available on the Workbook
instance.

The ``rows()`` method will hand out an iterator to read the worksheet rows. The
Worksheet object is also directly iterable and is equivalent to calling
``rows()``.

.. code:: python

   # You can use .rows(sparse=False) to include empty rows
   for row in sheet.rows():
       print(row)
   # [Cell(r=0, c=0, v='TEXT'), Cell(r=0, c=1, v=42.1337)]

*NOTE*: Iterating the same Worksheet instance multiple times in parallel (nested
``for`` for instance) will yield unexpected results, retrieve more instances
using ``get_sheet`` above.

Note that dates will appear as floats. You must use the ``convert_date(date)``
method from the corresponding Workbook instance to turn them into ``datetime``.

.. code:: python

   from pyxlsb import convert_date
   print(convert_date(41235.45578))
   # datetime.datetime(2012, 11, 22, 10, 56, 19)

*NOTE*: Using the ``convert_date`` in the ``pyxlsb`` module still works, but is
deprecated and will be removed.

Example
-------

Converting a workbook to CSV:

.. code:: python

   import csv
   from pyxlsb import open_workbook

   with open_workbook('Book1.xlsb') as wb:
       for name in wb.sheets:
           with wb.get_sheet(name) as sheet, open(name + '.csv', 'w') as f:
               writer = csv.writer(f)
               for row in sheet.rows():
                   writer.writerow([c.v for c in row])

Limitations
-----------

Non exhaustive list of things that are currently not supported:

-  Formulas

   -  Parsing *WIP*
   -  Evaluation

-  Style and formatting *WIP*
-  Rich text cells (formatting is lost, but getting the text works)
-  Encrypted (password protected) workbooks
-  Comments and other annotations
-  Writing (*very* far goal)

Feel free to open issues or, even better, submit PRs for these things and
anything else I might have missed, I'll try to prioritize what's most requested.

.. |PyPI| image:: https://img.shields.io/pypi/v/pyxlsb.svg
   :target: https://pypi.python.org/pypi/pyxlsb
.. |Build Status| image:: https://travis-ci.org/wwwiiilll/pyxlsb.svg?branch=master
   :target: https://travis-ci.org/wwwiiilll/pyxlsb
