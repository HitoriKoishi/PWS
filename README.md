# Paperbase

Paperbase 是一个本地运行的个人论文工作站，使用 Python Tkinter 打开独立桌面窗口，不依赖浏览器。

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
```

## 启动

使用 uv 启动：

```powershell
uv run python paperbase.py
```

论文数据保存在项目目录下的 `paperbase_data.json`，不会上传到外部服务器。

论文数据保存在当前浏览器的本地存储中，不会上传到外部服务器。
