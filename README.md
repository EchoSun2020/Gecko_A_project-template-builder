# 🦎 Gecko - Project Template Builder

一个快速创建标准化项目文件夹结构的 Windows 桌面工具。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ 功能特点

- 🚀 **即用即走** - 创建完成后自动退出，不占用资源
- 📁 **多级子文件夹** - 支持最多三级子文件夹结构
- ⚙️ **可视化模板管理** - 内置模板编辑器，无需改代码
- 🎨 **现代 UI** - 基于 CustomTkinter 的深色主题界面
- 📦 **独立运行** - 打包成 EXE 后无需 Python 环境

## 📸 界面预览

主界面：
- Type（类型）下拉选择
- Detail（详情）文本输入
- Path（路径）可浏览更改
- ⚙️ 设置按钮 - 打开模板管理器
- 一键创建 + 自动退出

模板管理器（点击设置按钮）：
- 新建/编辑/删除项目类型
- 可视化编辑子文件夹结构（支持三级）
- 修改默认路径
- 实时保存到 `config.json`

## 🛠️ 安装使用

### 方式一：直接运行 Python

```bash
# 安装依赖
pip install customtkinter

# 运行
python project_template_builder.py
```

### 方式二：打包成 EXE（推荐）

双击运行 `build.bat`，或手动执行：

```bash
pip install pyinstaller customtkinter

pyinstaller --noconfirm --onefile --windowed ^
    --name "ProjectTemplateBuilder" ^
    --collect-all customtkinter ^
    project_template_builder.py
```

打包后的文件在 `dist/` 目录：
- `ProjectTemplateBuilder.exe` - 主程序
- `config.json` - 配置文件（需与 EXE 放在同一目录）

## 📝 配置说明

`config.json` 示例：

```json
{
    "default_path": "D:\\00working",
    "subfolder_config": {
        "ART": {
            "REF": {},
            "PS": {},
            "BLENDER": {
                "SCENES": {},
                "TEXTURES": {}
            },
            "OUTPUT": {}
        }
    }
}
```

- 修改 `config.json` 后**无需重新打包**，直接生效
- 也可以通过程序内的「⚙️ 设置」按钮可视化编辑

## 📂 生成的文件夹格式

```
YYYYMMDD_TYPE_DETAIL/
├── 子文件夹1/
│   ├── 三级文件夹A/
│   └── 三级文件夹B/
├── 子文件夹2/
└── ...
```

例如：`20251225_ART_Cyberpunk/`

## 📄 License

MIT License
