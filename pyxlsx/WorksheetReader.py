# from openpyxl
import traceback
from warnings import warn

# compatibility imports
from openpyxl.xml.functions import iterparse

# package imports
from .Cell import Cell  # use reinherited Cell
from openpyxl.cell import MergedCell  # use reinherited MergedCell

from openpyxl.worksheet._reader import WorksheetReader as _WorksheetReader
from .ReadOnlyCell import ReadOnlyCell

class WorksheetReader(_WorksheetReader):
    """
    Create a parser and apply it to a workbook
    """
    def __init__(self, ws, xml_source, shared_strings, data_only, read_only):
        super().__init__(ws, xml_source, shared_strings, data_only)
        self.read_only = read_only

    def bind_cells(self):
        for idx, row in self.parser.parse():
            for cell in row:
                style = self.ws.parent._cell_styles[cell['style_id']]
                c = Cell(self.ws, row=cell['row'], column=cell['column'], style_array=style)
                c._value = cell['value']
                c.data_type = cell['data_type']
                self.ws._cells[(cell['row'], cell['column'])] = c
        self.ws.formula_attributes = self.parser.array_formulae
        if self.ws._cells:
            self.ws._current_row = self.ws.max_row # use cells not row dimensions
    
    def bind_cells_read_only(self):
        for idx, row in self.parser.parse():
            for cell in row:
                c = ReadOnlyCell(self.ws, **cell)
                self.ws._cells[(cell['row'], cell['column'])] = c
        self.ws.formula_attributes = self.parser.array_formulae
        if self.ws._cells:
            self.ws._current_row = self.ws.max_row # use cells not row dimensions

    def bind_all(self):
        if self.read_only:
            self.bind_cells_read_only()
        else:
            self.bind_cells()
        self.bind_merged_cells()
        self.bind_hyperlinks()
        self.bind_formatting()
        self.bind_col_dimensions()
        self.bind_row_dimensions()
        self.bind_tables()
        self.bind_properties()