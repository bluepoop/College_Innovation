# broad_table：图片颜色提取与表格处理

复用 `broad_dectector` 的 YOLO 检测、光照标准化、RGB/HSL 提取和 Excel 生成，使用根目录 `table` 的 Tkinter 表格编辑器处理结果。默认使用仓库内的 `broad_dectector/results/well_detection/weights/best.pt`，不需要重新训练。

## 启动

在仓库根目录执行（Python 3.10+）：

```powershell
python -m pip install -r dev/broad_table/requirements.txt
python dev/broad_table/main.py
```

也可双击 `run.bat`。源码运行需要仓库里的 `table/`、`broad_dectector/` 和训练权重。

## Windows EXE

双击 `dist/broad_table.exe` 即可运行。它是单文件程序，已内置默认检测模型、Python 和图像识别依赖，不需要另外安装 Python 或复制项目源码。首次启动需要解压运行库，可能需要等待一会儿。

重新打包可运行 `build.bat`，或在本目录执行 `python -m PyInstaller --clean --noconfirm broad_table.spec`。构建目录和 EXE 不纳入 Git。

## 使用

1. 点击“导入图片并提取表格”，选择 JPG、PNG、BMP 或 TIFF 孔板图片。识别在后台进行，期间可以移动或关闭窗口。
2. 左侧自动载入原检测程序的“RGB布局”和“数据表”，通过下拉框切换。默认 8 × 12 的 96 孔板；不用于通用图片表格 OCR。
3. 右侧等比例显示原图，可开关孔位框：绿色为检测孔，橙色为网格推算孔。数量会在顶部说明。图片颜色提取沿用原程序的光照标准化结果，预览显示原图。
4. 保留 table 的全部处理功能：固定/等差/等比标签、首末项或公差/公比输入、局部范围、单元格双击编辑、行列增删、撤销、项目保存和打开、其他表格文件导入。
5. 点击左侧“导出表格”：XLSX 导出全部工作表，CSV 导出当前工作表；单元格内容包含【标签】。需要继续编辑独立标签时，保存 JSON 项目。

失败时保留上一次表格和图片；重新导入图片前会提醒保存未保存修改。导入独立表格/JSON 后会清除旧图，避免与新表混淆。JSON 项目仅保存表格和标签，不保存原图及检测框。表格编辑不会重新计算图像检测结果。

## 说明与验证

- 直接读取原检测程序生成的临时 Excel，保留两张表的数据；沿用 table 的文本处理方式，不保留 Excel 原有填充色与样式。
- 网格会补齐 96 个孔位，推算孔和图外无有效颜色的孔需人工核对；不会把无有效颜色的数据填成 0。
- 默认模型在仓库内，可用“选择检测模型”切换。中文图片路径受支持。
- `pipeline.py` 不依赖界面，便于后续整合进 chemDb；`main.py` 负责左右布局和后台任务。

```powershell
python -m unittest discover -s table -p "test_*.py"
python -m unittest dev.broad_table.test_pipeline
python dev/broad_table/check_gui.py
```

最后一项会打开真实窗口，使用仓库测试图片执行检测、编辑、撤销和导出，然后自动关闭。
