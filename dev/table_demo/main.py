"""Standalone Tkinter demo; TableDemo can also be embedded in a Toplevel."""
import copy
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from core import Sheet, export_tables, load_project, load_tables, save_project


class TableDemo(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        self.pack(fill='both', expand=True)
        self.sheets = [Sheet('示例', [['样品', '浓度', '吸光度'], ['A', '0.1', '0.23'], ['B', '0.2', '0.45'], ['C', '0.4', '0.81']])]
        self.history = []
        self.label_dialog = None
        self.dirty = False
        bar = ttk.Frame(self)
        bar.pack(fill='x')
        for title, command in [('导入表格', self.import_file), ('打开标签项目', self.open_project), ('保存标签项目', self.save), ('撤销标签操作', self.undo), ('清空当前表标签', self.clear)]:
            ttk.Button(bar, text=title, command=command).pack(side='left', padx=3)
        self.sheet_choice = ttk.Combobox(bar, state='readonly', width=18)
        ttk.Button(bar, text='导出表格', command=self.export).pack(side='left', padx=3)
        self.sheet_choice.pack(side='right')
        self.sheet_choice.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        ttk.Label(self, text='点击每行左侧或每列上方的“＋标签”，选择类型后输入参数。原始内容保留；编号包含表头。').pack(anchor='w', pady=8)
        body = ttk.Frame(self)
        body.pack(fill='both', expand=True)
        self.table = tk.Canvas(body, background='white', highlightthickness=0)
        self.grid_frame = ttk.Frame(self.table)
        self.table.create_window((0, 0), window=self.grid_frame, anchor='nw')
        self.grid_frame.bind('<Configure>', lambda e: self.table.configure(scrollregion=self.table.bbox('all')))
        vertical = ttk.Scrollbar(body, orient='vertical', command=self.table.yview)
        horizontal = ttk.Scrollbar(body, orient='horizontal', command=self.table.xview)
        self.table.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.table.grid(row=0, column=0, sticky='nsew')
        vertical.grid(row=0, column=1, sticky='ns')
        horizontal.grid(row=1, column=0, sticky='ew')
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)
        self.detail = tk.StringVar(value='点击单元格查看完整内容和标签。')
        ttk.Label(self, textvariable=self.detail, wraplength=1050).pack(anchor='w', pady=8)
        self.status = tk.StringVar()
        ttk.Label(self, textvariable=self.status).pack(anchor='w')
        self.reset_choices()

    @property
    def sheet(self):
        return self.sheets[max(0, self.sheet_choice.current())]

    def reset_choices(self):
        self.sheet_choice['values'] = [s.name for s in self.sheets]
        self.sheet_choice.current(0)
        self.history.clear()
        self.dirty = False
        self.refresh()

    def refresh(self):
        sheet = self.sheet
        for child in self.grid_frame.winfo_children():
            child.destroy()
        for c in range(1, sheet.width + 1):
            ttk.Button(self.grid_frame, text=f'第 {c} 列 ＋标签', command=lambda c=c: self.open_labels('column', c)).grid(row=0, column=c, sticky='ew')
        for r, row in enumerate(sheet.rows, 1):
            ttk.Button(self.grid_frame, text=f'第 {r} 行 ＋标签', command=lambda r=r: self.open_labels('row', r)).grid(row=r, column=0, sticky='nsew')
            for c, value in enumerate(row, 1):
                content = value + ''.join(f' 【{tag}】' for tag in sheet.labels.get((r, c), []))
                cell = tk.Label(self.grid_frame, text=content, background='white', foreground='black', width=26, height=2, anchor='w', relief='solid', borderwidth=1)
                cell.grid(row=r, column=c, sticky='nsew')
                cell.bind('<Button-1>', lambda e, r=r, c=c: self.detail.set(f'第 {r} 行，第 {c} 列 | 原始内容：{self.sheet.rows[r-1][c-1]} | 标签：' + '、'.join(self.sheet.labels.get((r, c), []))))
        self.status.set(f'{sheet.name}：{len(sheet.rows)} 行 × {sheet.width} 列；{len(sheet.labels)} 个单元格有标签' + ('；有未保存修改' if self.dirty else ''))

    def open_labels(self, axis, index):
        if self.label_dialog is not None and self.label_dialog.winfo_exists():
            self.label_dialog.destroy()
        self.label_dialog = LabelDialog(self, axis, index)

    def confirm_discard(self):
        return not self.dirty or messagebox.askyesno('未保存修改', '标签尚未保存，确定放弃这些修改？', parent=self)

    def import_file(self):
        if not self.confirm_discard():
            return
        path = filedialog.askopenfilename(filetypes=[('表格文件', '*.xlsx *.xls *.csv *.tsv *.txt *.xml')])
        if path:
            self.try_load(path, load_tables)

    def open_project(self):
        if not self.confirm_discard():
            return
        path = filedialog.askopenfilename(filetypes=[('标签项目', '*.json')])
        if path:
            self.try_load(path, load_project)

    def try_load(self, path, loader):
        try:
            sheets = loader(path)
            self.sheets = sheets
            self.reset_choices()
        except Exception as exc:
            messagebox.showerror('导入失败', str(exc), parent=self)

    def save(self):
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('标签项目', '*.json')])
        if path:
            try:
                save_project(path, self.sheets)
                self.dirty = False
                self.refresh()
            except Exception as exc:
                messagebox.showerror('保存失败', str(exc), parent=self)

    def export(self):
        path = filedialog.asksaveasfilename(
            parent=self, title='导出表格（原始内容＋标签）',
            defaultextension='.xlsx',
            filetypes=[('Excel：全部工作表', '*.xlsx'), ('CSV：当前工作表', '*.csv')])
        if path:
            try:
                from pathlib import Path
                sheets = [self.sheet] if Path(path).suffix.lower() == '.csv' else self.sheets
                export_tables(path, sheets)
                messagebox.showinfo('导出成功', f'已导出到：\n{path}\n\n单元格包含原始内容和【标签】。\n若需继续编辑独立标签，请同时保存标签项目。', parent=self)
            except Exception as exc:
                messagebox.showerror('导出失败', str(exc), parent=self)

    def clear(self):
        self.history.append((self.sheet, copy.deepcopy(self.sheet.labels)))
        self.sheet.labels.clear()
        self.dirty = True
        self.refresh()

    def undo(self):
        if self.history:
            sheet, labels = self.history.pop()
            sheet.labels = labels
            self.sheet_choice.current(self.sheets.index(sheet))
            self.dirty = True
            self.refresh()

class LabelDialog(tk.Toplevel):
    def __init__(self, app, axis, index):
        super().__init__(app)
        self.withdraw()
        self.app, self.axis, self.index = app, axis, index
        self.target_sheet = app.sheet
        self.length = app.sheet.width if axis == 'row' else len(app.sheet.rows)
        self.title(f'第 {index} {"行" if axis == "row" else "列"}添加标签')
        self.configure(background='white')
        self.resizable(False, False)
        self.transient(app.winfo_toplevel())
        # Do not capture all application input: an obscured dialog must never
        # prevent the user from interacting with or closing the main window.
        self.protocol('WM_DELETE_WINDOW', self.destroy)
        self.bind('<Escape>', lambda event: self.destroy())
        self.mode = 'fixed'
        self.method = tk.StringVar(value='step')
        self.values = {key: tk.StringVar(value=value) for key, value in {
            'text': '', 'first': '1', 'step': '1', 'last': '10', 'suffix': '',
            'start': '1', 'end': str(self.length)}.items()}
        self.panel = ttk.Frame(self, padding=18)
        self.panel.pack(fill='both', expand=True)
        self.show_types()
        self.update_idletasks()
        parent = app.winfo_toplevel()
        x = max(0, min(parent.winfo_rootx() + 60, self.winfo_screenwidth() - 480))
        y = max(0, min(parent.winfo_rooty() + 60, self.winfo_screenheight() - 600))
        self.geometry(f'+{x}+{y}')
        self.deiconify()
        self.lift()
        self.after_idle(self.focus_set)

    def empty_panel(self):
        for child in self.panel.winfo_children():
            child.destroy()

    def show_types(self):
        self.empty_panel()
        ttk.Label(self.panel, text='请选择添加类型').pack(anchor='w', pady=8)
        for name, mode in [('固定标签', 'fixed'), ('等差数列', 'arithmetic'), ('等比数列', 'geometric')]:
            ttk.Button(self.panel, text=name, command=lambda mode=mode: self.choose(mode)).pack(fill='x', pady=4)

    def choose(self, mode):
        self.mode = mode
        self.show_form()

    def entry(self, title, key):
        row = ttk.Frame(self.panel)
        row.pack(fill='x', pady=4)
        ttk.Label(row, text=title, width=20).pack(side='left')
        entry = ttk.Entry(row, textvariable=self.values[key], width=30)
        entry.pack(side='right')
        return entry

    def show_form(self):
        self.empty_panel()
        mode = self.mode
        ttk.Label(self.panel, text={'fixed': '固定标签', 'arithmetic': '等差数列', 'geometric': '等比数列'}[mode]).pack(anchor='w', pady=6)
        first_entry = self.entry('标签文字' if mode == 'fixed' else '前缀（可留空）', 'text')
        if mode != 'fixed':
            delta = '公差' if mode == 'arithmetic' else '公比'
            for title, value in [(f'首项 ＋ {delta}', 'step'), ('从起点到终点（按格子数分配）', 'endpoints')]:
                ttk.Radiobutton(self.panel, text=title, variable=self.method, value=value, command=self.show_form).pack(anchor='w')
            self.entry('首项 / 起点', 'first')
            self.entry(delta if self.method.get() == 'step' else '终点（包含）', 'step' if self.method.get() == 'step' else 'last')
            self.entry('后缀 / 单位（可留空）', 'suffix')
            ttk.Label(self.panel, text='起止模式按所选格子数计算公差/公比；等比起止需非零且同号。', wraplength=410).pack(anchor='w', pady=6)
        direction = '列' if self.axis == 'row' else '行'
        ttk.Label(self.panel, text='默认覆盖整行/整列（含表头），可调整范围：').pack(anchor='w', pady=(12, 3))
        self.entry(f'从第几{direction}', 'start')
        self.entry(f'到第几{direction}', 'end')
        self.preview = tk.StringVar(value='')
        ttk.Label(self.panel, textvariable=self.preview, wraplength=410).pack(anchor='w', pady=8)
        bar = ttk.Frame(self.panel)
        bar.pack(fill='x')
        ttk.Button(bar, text='返回类型', command=self.show_types).pack(side='left')
        ttk.Button(bar, text='预览', command=self.preview_labels).pack(side='left', padx=6)
        ttk.Button(bar, text='添加', command=self.submit).pack(side='right')
        first_entry.focus_set()

    def parameters(self):
        v = {key: var.get() for key, var in self.values.items()}
        start, end = int(v['start']), int(v['end'])
        if not 1 <= start <= end <= self.length:
            raise ValueError(f'范围需在 1 到 {self.length} 之间，起点不能大于终点')
        values = {key: v[key] for key in ('text', 'first', 'step', 'suffix')}
        if self.mode != 'fixed' and self.method.get() == 'endpoints':
            values['last'] = v['last']
            values['step'] = '1'
        return start, end, values

    def preview_labels(self):
        try:
            from core import make_labels
            start, end, values = self.parameters()
            tags = make_labels(end - start + 1, self.mode, **values)
            shown = tags if len(tags) <= 6 else tags[:3] + ['…'] + tags[-2:]
            self.preview.set(f'共 {len(tags)} 个标签：' + '、'.join(shown))
        except (ValueError, ArithmeticError) as exc:
            self.preview.set(str(exc))

    def submit(self):
        try:
            if self.app.sheet is not self.target_sheet:
                raise ValueError('工作表已切换或重新导入，请关闭此窗口并重新点击目标行/列')
            start, end, values = self.parameters()
            before = copy.deepcopy(self.app.sheet.labels)
            self.app.sheet.annotate(self.axis, self.index, start, end, self.mode, **values)
            self.app.history.append((self.app.sheet, before))
            self.app.dirty = True
            self.app.refresh()
            self.destroy()
        except (ValueError, ArithmeticError) as exc:
            self.preview.set(str(exc))


def main():
    root = tk.Tk()
    root.title('chemDb 表格标签 Demo')
    root.geometry('1200x700')
    root.configure(background='white')
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', background='white', foreground='black', fieldbackground='white')
    style.configure('Treeview', rowheight=30)
    app = TableDemo(root)
    root.protocol('WM_DELETE_WINDOW', lambda: root.destroy() if app.confirm_discard() else None)
    root.mainloop()


if __name__ == '__main__':
    main()
