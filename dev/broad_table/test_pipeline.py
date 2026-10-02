import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from table.core import export_tables, load_project, load_tables, save_project
from dev.broad_table.pipeline import ROOT, extract_tables


class PipelineTests(unittest.TestCase):
    def test_detector_excel_to_editable_tables_and_export(self):
        from broad_dectector.scripts.process_wells import WellProcessor
        processor = WellProcessor.__new__(WellProcessor)
        payload = json.loads((ROOT / 'broad_dectector/results/1_results.json').read_text(encoding='utf-8'))
        processor.process_image = Mock(return_value=payload['wells'])
        sheets, wells = extract_tables(ROOT / 'broad_dectector/test_img/1.jpg', processor=processor)
        self.assertEqual([s.name for s in sheets], ['RGB布局', '数据表'])
        self.assertEqual(len(sheets[1].rows), len(wells) + 1)
        sheet = sheets[1]
        sheet.annotate('column', 4, 2, 4, 'arithmetic', text='sample=', first='1', step='1')
        sheet.set_cell(2, 4, '123')
        sheet.resize('row', 2)
        self.assertEqual(sheet.labels[3, 4], ['sample=1'])
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            save_project(directory / 'p.json', sheets)
            self.assertEqual(load_project(directory / 'p.json'), sheets)
            export_tables(directory / 'out.xlsx', sheets)
            loaded = load_tables(directory / 'out.xlsx')
            self.assertEqual(loaded[1].rows[1][3], '123 【sample=1】')
        processor.process_image.assert_called_once()

    def test_insufficient_detection_does_not_fabricate_table(self):
        processor = Mock()
        for wells in ([], [{'row': -1, 'col': -1}]):
            processor.process_image.return_value = wells
            with self.assertRaises(ValueError):
                extract_tables(ROOT / 'broad_dectector/test_img/1.jpg', processor=processor)
        processor.save_excel.assert_not_called()


if __name__ == '__main__':
    unittest.main()
