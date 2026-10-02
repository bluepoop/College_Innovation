"""Adapter for the existing detector's Excel output; no GUI dependencies."""
from pathlib import Path
from tempfile import TemporaryDirectory

from table.core import load_tables

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = ROOT / 'broad_dectector/results/well_detection/weights/best.pt'


def extract_tables(image_path, model_path=DEFAULT_MODEL, processor=None):
    """Return the same RGB layout/detail sheets as the detector and raw wells."""
    image_path = Path(image_path)
    if not image_path.is_file():
        raise ValueError('图片文件不存在')
    if processor is None:
        if not Path(model_path).is_file():
            raise ValueError('找不到模型，请选择训练好的 best.pt 文件')
        from broad_dectector.scripts.process_wells import WellProcessor
        processor = WellProcessor(str(model_path))
    wells = processor.process_image(image_path, save_results=False)
    if not wells:
        raise ValueError('没有识别到孔位，请换一张清晰的孔板图片')
    if not any(well.get('row', -1) >= 0 for well in wells):
        raise ValueError('检测到的孔位不足，无法确定孔板行列，请换一张包含完整孔板的图片')
    with TemporaryDirectory(prefix='broad_table_') as directory:
        output = Path(directory) / 'detected.xlsx'
        processor.save_excel(wells, str(output), image_path.stem)
        sheets = load_tables(output)
    return sheets, wells
