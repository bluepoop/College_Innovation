# 项目总览

本仓库包含以下项目和开发目录：

- `broad_dectector/`：96 孔板检测与 RGB 颜色提取项目。使用 YOLO 识别孔位，并输出检测和颜色分析结果。具体使用方法见 [项目说明](broad_dectector/README.md)。
- `chemDb/`：小组共享的文字与附件数据库，包含 Windows 客户端及相关打包文件。服务端部署、客户端配置和使用说明见 [项目说明](chemDb/README.md)。
- `table/`：独立的表格处理程序，支持文件导入、行列与单元格编辑、批量标签及导出，见 [项目说明](table/README.md)。
- `dev/`：开发目录；其中 [`broad_table`](dev/broad_table/README.md) 整合孔板图片识别与 table，左侧编辑提取表格、右侧查看图片。
