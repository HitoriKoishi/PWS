# Paperbase 项目手册

最后更新：2026-08-29

最近变更：从 Tkinter 迁移到 PySide6（Qt）。输入法（IME）预编辑拼音由 Qt 原生内联处理，不再出现 Tkinter 组合窗口白色浮层问题；输入框字体统一为 Segoe UI。

## 1. 项目定位

Paperbase 是一个 Windows 本地论文整理工具。当前桌面版本使用 Python + PySide6（Qt），启动入口是 `paperbase.py`，数据保存在项目目录的 `paperbase_data.json`。

桌面版本不依赖浏览器，也不需要本地 HTTP 服务。`index.html`、`styles.css` 和 `app.js` 是早期网页原型文件，目前不是桌面程序的启动路径。

## 2. 目录结构

```text
paperbase.py              桌面程序启动入口
paperbase/                Python 应用包
  __init__.py             包版本信息
  app.py                  主窗口、布局和用户交互
  config.py               路径、字体、颜色和界面常量
  models.py               Paper 数据模型和示例数据
  storage.py              JSON 数据读取、保存和 ID 管理
  theme.py                Qt 样式表（QSS）和通用按钮工厂
  widgets.py              可滚动容器和论文卡片
  dialogs.py              新建 / 编辑论文窗口
  window_state.py         编辑窗口尺寸和位置持久化
paperbase_data.json       运行时生成的本地论文数据
pyproject.toml            uv 项目配置
uv.lock                   uv 锁定文件
start.bat                 Windows 双击启动脚本
README.md                 快速上手说明
PROJECT_MANUAL.md         本手册
.gitignore                本地缓存和用户数据忽略规则
```

## 3. 文件职责

### `paperbase.py`

只负责调用 `paperbase.app.run()`。不要把数据逻辑、Qt 布局或业务操作重新写回这个文件。

### `paperbase/app.py`

负责主窗口生命周期和页面交互，包括：

- 创建侧边栏、论文目录、PDF 预览面板和详情区域
- 管理当前论文、状态筛选、标签筛选和搜索条件
- 从现有论文动态统计标签，并维护侧边栏标签列表
- 处理新增、编辑、删除、复制操作
- 调用 `PaperRepository` 保存数据
- 调用 `PaperCard` 和 `ScrollableFrame` 渲染列表

选中论文时只更新卡片选中状态和右侧详情，不重建整个目录，因此不会造成闪烁或滚动位置跳回顶部。

标签栏不保存独立的静态配置，而是从 `Paper.tags` 实时计算：默认显示使用次数最多的 8 个标签；超过 8 个时通过“查看全部标签”打开可滚动选择窗口。新增、编辑标签、删除论文或复制论文后，统一通过 `render()` 立即刷新标签计数和筛选状态。

选中已经显示在侧边栏的标签时，只更新按钮文案和选中颜色，不销毁按钮控件；只有标签集合或展示顺序发生变化时才重建标签栏，避免刷新期间销毁正在交互的控件。

详情页包含 PDF 内嵌预览面板，基于 `QPdfView` + `QPdfDocument` 实现：切换选中论文时自动加载或清除对应 PDF；文件缺失或加载失败时在面板上方显示状态提示；支持 `FitToWidth` 缩放和多页滚动；「在外部打开」按钮通过系统默认 PDF 阅读器打开。

### `paperbase/config.py`

集中管理数据路径、字体、调色板、状态文案和三类内容块样式。修改颜色或字段块对比度时优先修改这里，不要在多个 UI 文件中复制颜色值。

`FONT` 是界面通用字体（Microsoft YaHei UI），`INPUT_FONT` 是输入框字体（Segoe UI）。Qt 的 QLineEdit / QTextEdit 使用 `INPUT_FONT`，中文输入法预编辑拼音会以该字体内联显示。

### `paperbase/models.py`

定义 `Paper` dataclass，负责：

- 统一论文字段（含可选的 `pdf_path` 本地 PDF 路径）
- 在字典和对象之间转换（旧数据无 `pdf_path` 时自动兼容为空字符串）
- 生成搜索用的文本（包含 PDF 文件名）
- 提供首次运行的示例论文

新增论文字段时，应先在 `Paper` 中增加，再同步更新 `dialogs.py` 和 `storage.py` 的兼容逻辑。

`updated` 字段暂时保留用于兼容已有 JSON 数据，但不在界面显示；详情页只显示稳定的编辑日期 `date`。

### `paperbase/storage.py`

负责本地 JSON 文件读写。保存时先写入 `.tmp` 文件，再替换正式文件，降低程序中断导致 JSON 损坏的风险。UI 层不应直接调用 `Path.read_text` 或 `Path.write_text`。

### `paperbase/theme.py`

负责 Qt 样式表（QSS）和通用扁平按钮。`build_qss()` 集中定义全局样式，`setup(app)` 将样式应用到 `QApplication`。通用按钮应优先使用 `flat_button`，通过 `object_name` 选择 QSS 中的按钮样式（如 `PrimaryButton`、`GhostButton`、`DangerButton`、`StatusButton`）。

### `paperbase/widgets.py`

包含两个可复用控件：

- `ScrollableFrame`：基于 `QScrollArea` 的垂直滚动容器，通过 `add_widget` 添加子控件
- `PaperCard`：论文目录卡片和选中状态，点击卡片触发选择回调

Qt 的 `QScrollArea` 原生支持滚轮，无需手动绑定滚轮事件。

### `paperbase/dialogs.py`

负责新建和编辑论文。编辑窗口包含自己的表单滚动区和固定底部操作栏；概要、创新点和我的笔记分别使用独立的文本滚动条。校验规则包括：

- 论文名称不能为空
- 会议 / 期刊不能为空
- 年份必须是数字

窗口使用 `window_state.py` 计算屏幕可用空间，确保编辑字段和滚动条有足够的显示区域；关闭时保存窗口大小和位置，下一次新建或编辑时恢复。

### `paperbase/window_state.py`

负责编辑窗口的尺寸和位置：

- 首次打开时根据屏幕尺寸选择默认大小
- 对历史过小或超出屏幕的窗口状态进行约束
- 在取消、保存或右上角关闭时保存几何信息
- 状态文件为 `paperbase_window_state.json`，属于本地运行时文件

保存成功后通过 `PaperEditor.result` 返回新的 `Paper` 对象，主窗口再按论文 ID 替换记录。

### `pyproject.toml`

定义 uv 项目名称、版本、Python 版本要求和依赖。当前依赖 `pyside6`，由 uv 管理。

### `start.bat`

执行 `uv run python paperbase.py`。桌面程序需要从项目目录启动，保证数据文件路径稳定。

### `paperbase_data.json`

运行时用户数据文件，不应手动修改结构。该文件已加入 `.gitignore`，删除后程序会恢复示例论文。

### `README.md`

面向使用者的快速说明。每次功能更新、启动方式变化、数据结构变化或已知问题变化时同步更新。

### `PROJECT_MANUAL.md`

面向维护者的详细说明。每次新增、删除或拆分文件，以及修改模块职责时同步更新。

### `index.html`、`styles.css`、`app.js`、`package.json`

这些文件属于早期网页原型，目前不参与 PySide6 桌面版本启动。除非明确恢复网页版本，否则不要将桌面功能修改分散到这些文件中。

## 4. 数据流

```text
paperbase.py
    ↓
app.run()
    ↓
PaperbaseApp
    ├─ PaperRepository.load() 读取 JSON
    ├─ PaperCard 渲染论文目录
    ├─ PaperEditor 返回修改后的 Paper
    └─ PaperRepository.save() 写回 JSON
```

## 5. 更新规范

每次修复或新增功能后执行：

```powershell
uv run python -m compileall -q paperbase.py paperbase
```

涉及窗口初始化、编辑、删除或滚动容器时，还应运行 Qt 烟雾测试，至少确认：

1. 主窗口可以创建。
2. 目录和详情滚动互不干扰。
3. 编辑窗口保存后论文内容改变。
4. 删除后选中项和列表内容同步。
5. 长文本可以通过滚动条完整查看。
6. 标签筛选结果不足一屏时，目录滚动条不会移动。

完成代码修改后，必须同步维护：

- `README.md`：用户可见功能、启动方式和验证命令
- `PROJECT_MANUAL.md`：文件职责、架构和维护规则
