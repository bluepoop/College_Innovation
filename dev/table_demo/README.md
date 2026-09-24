# chemDb 表格标签 Demo

沿用 chemDb 客户端的 Python 3.10+、Tkinter，只有简洁的白底黑字窗口，无需服务器。

在仓库根目录运行：

```powershell
python -m pip install -r dev/table_demo/requirements.txt
python dev/table_demo/main.py
```

启动时自带一张示例表，也可导入 `examples` 下的文件。

## Windows EXE

双击 `dist/chemDb-table-demo.exe` 即可运行，无需安装 Python。分发时只需复制这个 EXE。
开发环境需要重新打包时，运行本目录的 `build.bat`，生成单文件、无控制台窗口的 EXE。

## 功能

- 导入 XLSX（多工作表）、XLS、CSV、TSV、分隔符 TXT、XML。文本支持 UTF-8 和 GB18030。
- 点击每行左侧或每列顶部的“＋标签”，先选择固定标签、等差、等比，再输入参数。编号从 1 开始，**包含表头**；弹窗默认覆盖整行/整列，可调整格子范围。
- 数列可选“首项＋公差/公比”或“从起点到终点”。起止模式按目标格子数分配并包含两端；等比起止要求两端非零且同号，采用正公比。
- 固定模式：每个目标单元格添加相同字符串。
- 等差模式：首项 + 公差 × 序号；等比模式：首项 × 公比的序号次方。序号从选定范围的起点开始计为 0。
- 数列模式支持前缀和后缀，例如 `浓度=` + `0.1、0.2、0.3` + ` mM`。采用 Decimal，最多 50 位有效数字。
- 标签独立于原始内容；重复操作可以叠加不同标签，同一单元格相同标签去重。支持撤销和清空当前工作表标签。
- 保存标签项目为 JSON，包含全部工作表的原始内容和单元格标签，可重新打开。
- 点击“导出表格”：Excel（XLSX）导出全部工作表，CSV 导出当前工作表（UTF-8 BOM）。单元格按 `原始内容 【标签】` 导出，XLSX 中作为文字保存，不计算公式。导出后标签成为单元格文字；需要继续独立编辑标签时，请同时保存 JSON 标签项目。

### 快速体验

启动后点击“第 2 列 ＋标签”，选择“等比数列”，前缀填 `浓度=`，首项 `0.1`，公比 `2`，后缀 ` mM`，格子范围填第 `2` 行到第 `4` 行。点击“预览”或“添加”，将得到 `浓度=0.1 mM`、`浓度=0.2 mM`、`浓度=0.4 mM`。也可选择起止模式，起点填 `0.1`、终点填 `0.4`。

## XML 范围

支持 Excel 2003 SpreadsheetML（含命名空间、工作表、Row/Cell 的 Index 稀疏索引），以及两种平面结构：

```xml
<table><row><cell>A</cell><cell>1</cell></row></table>
```

```xml
<records><record><sample>A</sample><value>1</value></record></records>
```

第二种结构会根据字段名自动生成表头，缺失字段补空。任意嵌套 XML 不自动猜测映射；禁用实体解析。

## 后续集成

`core.py` 不依赖界面或网络，提供 `load_tables`、`Sheet.annotate`、`save_project` 和 `load_project`。`main.py` 的 `TableDemo` 是 Tkinter Frame，可嵌入 chemDb 窗口。JSON 可以作为现有 chemDb 记录的附件；此 demo 尚未连接数据库或上传接口。

当前用于小型表格功能验证，整张表在内存中展示；保留单元格文本，不保留 Excel 样式、合并布局、图表，也不计算公式（XLSX 显示公式文本）。项目保存格式为 JSON，可另行导出 XLSX 或 CSV。

运行测试：`python -m unittest discover -s dev/table_demo -p "test_*.py"`
