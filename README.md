# Paperbase

Paperbase 是一个本地运行的个人论文工作站，使用 Python + PySide6（Qt）打开独立桌面窗口，不依赖浏览器。

最后更新：2026-08-29

已从 Tkinter 迁移到 PySide6（Qt），输入法（IME）预编辑拼音由 Qt 原生内联处理，不再出现 Tkinter 组合窗口白色浮层问题。

## 目录结构

```text
paperbase.py              # 启动入口
paperbase/
  app.py                  # 主窗口与交互流程
  config.py               # 路径、颜色与界面常量
  models.py               # 论文数据模型与示例数据
  storage.py              # 本地 JSON 持久化
  theme.py                # Qt 样式表（QSS）和通用按钮工厂
  widgets.py              # 论文卡片和滚动容器
  dialogs.py              # 新建 / 编辑论文对话框
  window_state.py         # 编辑窗口尺寸与位置持久化
PROJECT_MANUAL.md         # 项目文件与维护手册
```

## 启动

使用 uv 启动：

```powershell
uv run python paperbase.py
```

也可以双击 `start.bat` 启动。

论文数据保存在项目目录下的 `paperbase_data.json`，不会上传到外部服务器。

## 当前功能

- 论文列表、搜索、状态筛选、标签筛选和排序
- 标签栏从现有论文动态生成，按使用次数排序并显示论文数量
- 标签过多时保留常用标签，并通过“查看全部标签”打开完整选择窗口
- 新建、编辑、删除、复制论文
- PDF 关联与内嵌预览：编辑窗口可选择本地 PDF，详情页直接内嵌阅读，支持多页滚动和自适应宽度，也可一键在外部打开
- 概要、创新点、我的笔记分块显示
- 详情页独立滚动条，支持较长文本
- 目录、详情和编辑窗口的鼠标滚轮互不干扰
- 筛选结果不足一屏时自动禁用目录滚动
- 详情页仅显示编辑日期，不显示容易过时的“刚刚更新”状态
- 新建和编辑窗口的概要、创新点、我的笔记各自拥有独立滚动条
- 编辑窗口自动适配屏幕尺寸，并记住上次关闭时的大小和位置
- 输入框使用 Segoe UI，中文输入法预编辑拼音由 Qt 原生内联显示
- 本地 JSON 自动保存

## 验证命令

```powershell
uv run python -m compileall -q paperbase.py paperbase
uv run python paperbase.py
```

更详细的文件职责、数据流和维护规范见 [PROJECT_MANUAL.md](PROJECT_MANUAL.md)。
