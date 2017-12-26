import os
import struct
from .recordhandlers import *
from .datareader import DataReader

uint8_t = struct.Struct('<B')

class RecordReader(object):
    default_handler = RecordHandler()

    handlers = {
        # Workbook part handlers
        records.WORKBOOK:   BasicRecordHandler('workbook'),
        records.SHEETS:     BasicRecordHandler('sheets'),
        records.SHEETS_END: BasicRecordHandler('/sheets'),
        records.SHEET:      SheetHandler(),

        # SharedStrings part handlers
        records.SST:     StringTableHandler(),
        records.SST_END: BasicRecordHandler('/sst'),
        records.SI:      StringInstanceHandler(),

        # Worksheet part handlers
        records.WORKSHEET:       BasicRecordHandler('worksheet'),
        records.WORKSHEET_END:   BasicRecordHandler('/worksheet'),
        records.DIMENSION:       DimensionHandler(),
        records.SHEETDATA:       BasicRecordHandler('sheetData'),
        records.SHEETDATA_END:   BasicRecordHandler('/sheetData'),
        records.COLS:            BasicRecordHandler('cols'),
        records.COLS_END:        BasicRecordHandler('/cols'),
        records.COL:             ColumnHandler(),
        records.ROW:             RowHandler(),
        records.BLANK:           CellHandler(),
        records.NUM:             CellHandler(),
        records.BOOLERR:         CellHandler(),
        records.BOOL:            CellHandler(),
        records.FLOAT:           CellHandler(),
        records.STRING:          CellHandler(),
        records.FORMULA_STRING:  FormulaCellHandler(),
        records.FORMULA_FLOAT:   FormulaCellHandler(),
        records.FORMULA_BOOL:    FormulaCellHandler(),
        records.FORMULA_BOOLERR: FormulaCellHandler(),
        records.HYPERLINK:       HyperlinkHandler()
    }

    def __init__(self, fp, _debug=False):
        super(RecordReader, self).__init__()
        self._debug = _debug
        self._fp = fp

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def tell(self):
        return self._fp.tell()

    def seek(self, offset, whence=os.SEEK_SET):
        self._fp.seek(offset, whence)

    def read_id(self):
        v = 0
        for i in range(4):
            byte = self._fp.read(1)
            if byte == '':
                return None
            byte = uint8_t.unpack(byte)[0]
            v += byte << 8 * i
            if byte & 0x80 == 0:
                break
        return v

    def read_len(self):
        v = 0
        for i in range(4):
            byte = self._fp.read(1)
            if byte == '':
                return None
            byte = uint8_t.unpack(byte)[0]
            v += (byte & 0x7F) << (7 * i)
            if byte & 0x80 == 0:
                break
        return v

    def register_handler(self, recid, handler):
        self.handlers[recid] = handler

    def next(self):
        ret = None
        while ret is None:
            if self._debug:
                pos = self._fp.tell()
            recid = self.read_id()
            reclen = self.read_len()
            if recid is None or reclen is None:
                raise StopIteration
            recdata = self._fp.read(reclen)
            ret = self.handlers.get(recid, self.default_handler).read(DataReader(recdata), recid, reclen)
            if self._debug:
                print('{:08X}  {:04X}  {:<6} {}\n{}'.format(pos, recid, reclen, ' '.join('{:02X}'.format(b) for b in recdata), ret))
        return (recid, ret)

    def close(self):
        self._fp.close()