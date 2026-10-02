"""Run from anywhere: python <repo>/dev/broad_table/main.py."""
from pathlib import Path
import queue
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

ROOT = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PIL import Image, ImageDraw, ImageOps, ImageTk
from table.core import Sheet
from table.main import TableDemo
from dev.broad_table.pipeline import DEFAULT_MODEL, extract_tables


class ImageTableEditor(TableDemo):
    def try_load(self, path, loader):
        previous = self.sheets
        super().try_load(path, loader)
        if self.sheets is not previous:
            self.on_external_load()


class BroadTable(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=8)
        self.pack(fill='both', expand=True)
        self.results = queue.Queue()
        self.busy = False
        self.closed = False
        self.original = None
        self.wells = []
        self.preview_photo = None
        self.model_path = tk.StringVar(value=str(DEFAULT_MODEL))
        self.show_boxes = tk.BooleanVar(value=True)
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', pady=(0, 6))
        self.import_button = ttk.Button(toolbar, text='导入图片并提取表格', command=self.import_image)
        self.import_button.pack(side='left')
        self.model_button = ttk.Button(toolbar, text='选择检测模型', command=self.choose_model)
        self.model_button.pack(side='left', padx=8)
        ttk.Label(toolbar, text='96 孔板（8 × 12）').pack(side='left')
        self.progress = ttk.Progressbar(toolbar, mode='indeterminate', length=120)
        self.progress.pack(side='right')
        self.notice = tk.StringVar(value='导入图片后，左侧显示提取表格，右侧显示原图。')
        ttk.Label(self, textvariable=self.notice, wraplength=1250).pack(anchor='w', pady=4)
        panes = ttk.Panedwindow(self, orient='horizontal')
        panes.pack(fill='both', expand=True)
        left = ttk.Frame(panes, width=800)
        right = ttk.Frame(panes, width=480, padding=8)
        panes.add(left, weight=3)
        panes.add(right, weight=2)
        self.editor = ImageTableEditor(left)
        self.editor.on_external_load = self.clear_image
        self.editor.sheets = [Sheet('待导入', [['请点击上方“导入图片并提取表格”']])]
        self.editor.reset_choices()
        self.overlay = ttk.Label(left, text='正在识别图片，请稍候…', anchor='center')
        ttk.Checkbutton(right, text='显示孔位框（绿：检测；橙：推算）', variable=self.show_boxes, command=self.render_image).pack(anchor='w')
        self.image_name = tk.StringVar(value='尚未导入图片')
        ttk.Label(right, textvariable=self.image_name, wraplength=420).pack(anchor='w', pady=6)
        self.canvas = tk.Canvas(right, background='white', highlightthickness=1)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind('<Configure>', lambda event: self.render_image())
        ttk.Label(right, text='颜色值沿用检测程序的光照标准化结果；右侧为原图。\n推算孔不代表实际检测成功，请结合图片核对。', wraplength=420).pack(anchor='w', pady=6)
        self.poll_id = self.after(100, self.poll)

    def choose_model(self):
        path = filedialog.askopenfilename(parent=self, title='选择训练好的孔板模型', filetypes=[('YOLO 模型', '*.pt')])
        if path:
            self.model_path.set(path)
            self.notice.set(f'检测模型：{Path(path).name}')

    def import_image(self):
        if self.busy:
            return
        if not self.editor.confirm_discard():
            return
        path = filedialog.askopenfilename(parent=self, title='选择孔板图片', filetypes=[('图片', '*.jpg *.jpeg *.png *.bmp *.tif *.tiff')])
        if path:
            self.start_image(path)

    def start_image(self, path):
        """Start only after the caller has confirmed replacing any edits."""
        if self.busy:
            return
        self.busy = True
        self.import_button.configure(state='disabled')
        self.model_button.configure(state='disabled')
        if self.editor.label_dialog is not None and self.editor.label_dialog.winfo_exists():
            self.editor.label_dialog.destroy()
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.lift()
        self.disabled_controls = []
        pending = [self.editor]
        while pending:
            widget = pending.pop()
            pending.extend(widget.winfo_children())
            if isinstance(widget, (ttk.Button, ttk.Combobox)):
                self.disabled_controls.append((widget, str(widget.cget('state'))))
                widget.configure(state='disabled')
        self.overlay.focus_set()
        # Take keyboard focus away from any previous table toolbar button.
        self.focus_set()
        self.progress.start(12)
        self.notice.set('正在加载模型并提取颜色…首次加载可能需要一段时间。')
        model = self.model_path.get()

        def worker():
            try:
                with Image.open(path) as source:
                    original = ImageOps.exif_transpose(source).convert('RGB')
                sheets, wells = extract_tables(path, model)
                self.results.put(('ok', (str(path), original, sheets, wells)))
            except Exception as exc:
                self.results.put(('error', str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def poll(self):
        if self.closed:
            return
        try:
            kind, payload = self.results.get_nowait()
        except queue.Empty:
            pass
        else:
            self.busy = False
            self.progress.stop()
            self.overlay.place_forget()
            for widget, state in self.disabled_controls:
                if widget.winfo_exists():
                    widget.configure(state=state)
            self.import_button.configure(state='normal')
            self.model_button.configure(state='normal')
            if kind == 'error':
                self.notice.set('提取失败，原表格与图片仍保留。')
                messagebox.showerror('图片提取失败', payload, parent=self)
            else:
                path, self.original, sheets, self.wells = payload
                self.editor.sheets = sheets
                self.editor.reset_choices()
                self.editor.dirty = True
                self.editor.refresh()
                inferred = sum(bool(well.get('inferred')) for well in self.wells)
                self.notice.set(f'已提取 {len(self.wells)} 个孔位，其中 {inferred} 个为推算。可切换 RGB布局 / 数据表，编辑后点击“导出表格”。')
                self.image_name.set(Path(path).name)
                self.render_image()
        self.poll_id = self.after(100, self.poll)

    def clear_image(self):
        self.original = None
        self.wells = []
        self.image_name.set('当前表格未关联图片')
        self.notice.set('已打开表格文件，可继续编辑并导出。')
        self.render_image()

    def render_image(self):
        self.canvas.delete('all')
        if self.original is None:
            self.canvas.create_text(20, 20, anchor='nw', text='原图预览', fill='black')
            return
        width, height = max(1, self.canvas.winfo_width() - 16), max(1, self.canvas.winfo_height() - 16)
        image = self.original.copy()
        image.thumbnail((width, height), Image.Resampling.LANCZOS)
        if self.show_boxes.get():
            draw = ImageDraw.Draw(image)
            sx, sy = image.width / self.original.width, image.height / self.original.height
            for well in self.wells:
                x1, y1, x2, y2 = well['bbox']
                box = (x1 * sx, y1 * sy, x2 * sx, y2 * sy)
                color = '#cf7200' if well.get('inferred') else '#008c36'
                draw.rectangle(box, outline=color, width=2)
                draw.text((max(0, box[0]), max(0, box[1] - 12)), well.get('well_id', '?'), fill=color)
        self.preview_photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2, image=self.preview_photo)

    def close(self):
        if self.editor.confirm_discard():
            self.closed = True
            self.after_cancel(self.poll_id)
            self.winfo_toplevel().destroy()


def main():
    root = tk.Tk()
    root.title('broad_table — 图片颜色提取与表格处理')
    root.geometry('1450x850')
    root.minsize(1000, 600)
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', background='white', foreground='black', fieldbackground='white')
    app = BroadTable(root)
    root.protocol('WM_DELETE_WINDOW', app.close)
    root.mainloop()


if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    if len(sys.argv) == 4 and sys.argv[1] == '--self-test':
        from dev.broad_table.self_test import run
        run(sys.argv[2], sys.argv[3])
    else:
        main()
