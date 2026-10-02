"""Exercise GUI commands without opening desktop windows."""
import copy
import unittest
from unittest.mock import Mock, patch

from core import Sheet
from main import TableDemo


class EditingTests(unittest.TestCase):
    def setUp(self):
        self.app = TableDemo.__new__(TableDemo)
        self.app.sheets = [Sheet('A', [['a', 'b'], ['c', 'd']], {(2, 2): ['tag']}),
                           Sheet('B', [['other']])]
        self.app.sheet_choice = Mock()
        self.app.sheet_choice.current.return_value = 0
        self.app.history = []
        self.app.dirty = False
        self.app.refresh = Mock()
        self.app.detail = Mock()

    def test_edit_resize_and_undo_across_sheets(self):
        app = self.app
        original = copy.deepcopy(app.sheet)
        with patch('main.simpledialog.askstring', return_value='edited'):
            app.edit_cell(2, 2)
        self.assertEqual(app.sheet.rows[1][1], 'edited')
        self.assertEqual(app.sheet.labels[2, 2], ['tag'])
        app.resize_sheet('row', 1)
        self.assertEqual(app.sheet.labels[3, 2], ['tag'])
        app.resize_sheet('column', 2, True)
        self.assertEqual(app.sheet.labels, {})
        app.sheet_choice.current.return_value = 1
        for _ in range(3):
            app.undo()
        self.assertEqual(app.sheets[0], original)
        self.assertEqual(app.sheets[1].rows, [['other']])
        app.sheet_choice.current.assert_called_with(0)

    def test_cancel_noop_and_invalid_input(self):
        app = self.app
        with patch('main.simpledialog.askstring', return_value=None):
            app.edit_cell(2, 2)
        with patch('main.simpledialog.askstring', return_value='d'):
            app.edit_cell(2, 2)
        with patch('main.messagebox.showerror') as error:
            app.edit_cell(0, 1)
            error.assert_called_once()
        self.assertEqual(app.history, [])
        self.assertFalse(app.dirty)

    def test_clear_and_annotation_undo(self):
        app = self.app
        original = copy.deepcopy(app.sheet)
        app.apply_change(lambda: app.sheet.annotate('row', 1, 1, 2, 'fixed', text='new'))
        app.clear()
        app.undo()
        self.assertEqual(app.sheet.labels[1, 1], ['new'])
        app.undo()
        self.assertEqual(app.sheet, original)
