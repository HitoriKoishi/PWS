# Paperbase

Paperbase 是一个本地运行的个人论文工作站，使用 Python Tkinter 打开独立桌面窗口，不依赖浏览器。

最后更新：2026-08-05

顶部操作区已简化为单独的新建论文按钮，不再显示无实际操作的 `⌘ K` 快捷键提示。

## 目录结构

```text
paperbase.py              # 启动入口
paperbase/
  app.py                  # 主窗口与交互流程
  config.py               # 路径、颜色与界面常量
  models.py               # 论文数据模型与示例数据
  storage.py              # 本地 JSON 持久化
  theme.py                # Tkinter 主题和按钮样式
  widgets.py              # 论文卡片和滚动容器
  dialogs.py              # 新建 / 编辑论文对话框
PROJECT_MANUAL.md         # 项目文件与维护手册
```

## 启动

使用 uv 启动：

```powershell
uv run python paperbase.py
```

也可以双击 `launch-paperbase.bat` 启动。

论文数据保存在项目目录下的 `paperbase_data.json`，不会上传到外部服务器。

## 当前功能

- 论文列表、搜索、状态筛选、标签筛选和排序
- 新建、编辑、删除、复制论文
- 概要、创新点、我的笔记分块显示
- 详情页独立滚动条，支持较长文本
- 目录、详情和编辑窗口的鼠标滚轮互不干扰
- 筛选结果不足一屏时自动禁用目录滚动
- 本地 JSON 自动保存

## 验证命令

```powershell
uv run python -m compileall -q paperbase.py paperbase
uv run python paperbase.py
```

更详细的文件职责、数据流和维护规范见 [PROJECT_MANUAL.md](PROJECT_MANUAL.md)。
