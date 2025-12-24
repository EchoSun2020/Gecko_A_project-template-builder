"""
项目模板构建器
========================
使用 customtkinter 构建的 GUI 工具，用于快速创建标准化项目文件夹结构。

配置文件：config.json（与 EXE 或 .py 同目录）
- 修改 config.json 后无需重新打包，直接生效！
- 支持最多三级子文件夹结构

作者: Auto-generated
日期: 2024-12-25
"""

import os
import sys
import json
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox


# ============================================================
# 配置加载/保存
# ============================================================

def get_app_dir():
    """获取程序所在目录（兼容 PyInstaller 打包后的 EXE）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def get_config_path():
    """获取配置文件路径"""
    return os.path.join(get_app_dir(), "config.json")


def load_config():
    """加载外部配置文件"""
    config_path = get_config_path()
    
    # 默认配置
    default_config = {
        "default_path": r"D:\00working",
        "subfolder_config": {
            "ART": {"REF": {}, "PS": {}, "BLENDER": {}, "OUTPUT": {}},
            "CODE": {"SRC": {}, "DOCS": {}, "ASSETS": {}, "BUILD": {}},
            "VIDEO": {"FOOTAGE": {}, "PR": {}, "AE": {}, "RENDER": {}},
            "WRITING": {"DRAFT": {}, "RESEARCH": {}, "ASSETS": {}, "FINAL": {}},
        }
    }
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            # 兼容旧版配置（列表格式 -> 字典格式）
            config = migrate_old_config(config)
            return config
    except FileNotFoundError:
        save_config(default_config)
        return default_config
    except json.JSONDecodeError as e:
        messagebox.showerror("配置错误", f"config.json 格式错误：\n{e}")
        sys.exit(1)


def migrate_old_config(config):
    """兼容旧版配置格式（递归将列表转换为字典）"""
    
    def convert_to_dict(data):
        """递归转换：列表 -> 字典"""
        if isinstance(data, list):
            # ["A", "B"] -> {"A": {}, "B": {}}
            return {item: {} for item in data}
        elif isinstance(data, dict):
            # 递归处理每个子项
            return {key: convert_to_dict(value) for key, value in data.items()}
        else:
            return {}
    
    subfolder_config = config.get("subfolder_config", {})
    config["subfolder_config"] = convert_to_dict(subfolder_config)
    return config


def save_config(config):
    """保存配置到文件"""
    config_path = get_config_path()
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


# 全局配置
CONFIG = load_config()


# ============================================================
# 模板管理窗口
# ============================================================

class TemplateManagerWindow(ctk.CTkToplevel):
    """模板管理窗口"""
    
    def __init__(self, parent, on_save_callback=None):
        super().__init__(parent)
        
        self.parent = parent
        self.on_save_callback = on_save_callback
        self.config = load_config()  # 重新加载最新配置
        self.current_type = None
        self.last_enter_time = 0  # 用于检测双击回车
        
        # 窗口设置
        self.title("⚙️ 模板管理")
        self.geometry("720x620")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.grab_set()
        
        # 居中显示
        self.center_window()
        
        # 创建界面
        self.create_widgets()
        
        # 绑定双击回车保存
        self.bind("<Return>", self.on_enter_pressed)
        
        # 加载第一个模板
        if self.config["subfolder_config"]:
            first_type = list(self.config["subfolder_config"].keys())[0]
            self.select_type(first_type)
    
    def on_enter_pressed(self, event):
        """检测双击回车"""
        import time
        current_time = time.time()
        # 如果两次回车间隔小于0.5秒，执行保存
        if current_time - self.last_enter_time < 0.5:
            self.save_all()
        self.last_enter_time = current_time
    
    def center_window(self):
        """居中显示窗口"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (360)
        y = (self.winfo_screenheight() // 2) - (310)
        self.geometry(f"720x620+{x}+{y}")
    
    def create_widgets(self):
        """创建界面"""
        # 主容器
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # 标题
        title = ctk.CTkLabel(main_frame, text="📋 模板管理", 
                             font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(0, 15))
        
        # 上半部分：类型列表 + 子文件夹编辑
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # 左侧：类型列表
        left_frame = ctk.CTkFrame(content_frame, width=180)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)
        
        type_label = ctk.CTkLabel(left_frame, text="项目类型", 
                                  font=ctk.CTkFont(size=14, weight="bold"))
        type_label.pack(pady=(10, 5))
        
        # 类型列表框
        self.type_listbox_frame = ctk.CTkScrollableFrame(left_frame, height=300)
        self.type_listbox_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.type_buttons = {}
        self.refresh_type_list()
        
        # 类型操作按钮
        type_btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        type_btn_frame.pack(fill="x", padx=5, pady=10)
        
        add_type_btn = ctk.CTkButton(type_btn_frame, text="➕ 新建", width=75,
                                     command=self.add_new_type, height=28)
        add_type_btn.pack(side="left", padx=2)
        
        del_type_btn = ctk.CTkButton(type_btn_frame, text="🗑️ 删除", width=75,
                                     command=self.delete_type, height=28,
                                     fg_color="#dc2626", hover_color="#b91c1c")
        del_type_btn.pack(side="right", padx=2)
        
        # 右侧：子文件夹编辑区
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # 类型名称编辑
        name_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        name_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(name_frame, text="类型名称:", 
                     font=ctk.CTkFont(size=13)).pack(side="left")
        
        self.type_name_entry = ctk.CTkEntry(name_frame, width=200,
                                            font=ctk.CTkFont(size=13))
        self.type_name_entry.pack(side="left", padx=(10, 0))
        
        rename_btn = ctk.CTkButton(name_frame, text="重命名", width=70,
                                   command=self.rename_type, height=28)
        rename_btn.pack(side="left", padx=(10, 0))
        
        # 子文件夹编辑区标题
        subfolder_title = ctk.CTkLabel(right_frame, 
                                       text="📁 子文件夹结构（支持三级）",
                                       font=ctk.CTkFont(size=13, weight="bold"))
        subfolder_title.pack(anchor="w", padx=15, pady=(10, 5))
        
        # 子文件夹编辑区（文本框）
        self.subfolder_text = ctk.CTkTextbox(right_frame, height=280,
                                             font=ctk.CTkFont(family="Consolas", size=12))
        self.subfolder_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # 格式提示
        hint_text = "格式：每行一个文件夹，用2空格缩进表示层级 | 双击回车=保存"
        hint_label = ctk.CTkLabel(right_frame, text=hint_text,
                                  font=ctk.CTkFont(size=11),
                                  text_color="gray", justify="left")
        hint_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        # ========== 底部区域 ==========
        bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=(10, 0))
        
        # 默认路径设置
        path_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        path_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(path_frame, text="默认路径:",
                     font=ctk.CTkFont(size=13)).pack(side="left")
        
        self.default_path_entry = ctk.CTkEntry(path_frame, width=350,
                                               font=ctk.CTkFont(size=12))
        self.default_path_entry.pack(side="left", padx=(10, 5), fill="x", expand=True)
        self.default_path_entry.insert(0, self.config.get("default_path", ""))
        
        browse_btn = ctk.CTkButton(path_frame, text="浏览", width=60,
                                   command=self.browse_default_path, height=28)
        browse_btn.pack(side="right")
        
        # ========== 大保存按钮 ==========
        save_btn = ctk.CTkButton(
            bottom_frame, 
            text="💾  保 存  (双击回车)", 
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.save_all,
            fg_color="#16a34a", 
            hover_color="#15803d"
        )
        save_btn.pack(fill="x", pady=(5, 0))
    
    def refresh_type_list(self):
        """刷新类型列表"""
        # 清除旧按钮
        for widget in self.type_listbox_frame.winfo_children():
            widget.destroy()
        self.type_buttons.clear()
        
        # 创建新按钮
        for type_name in self.config["subfolder_config"].keys():
            btn = ctk.CTkButton(
                self.type_listbox_frame,
                text=type_name,
                command=lambda t=type_name: self.select_type(t),
                height=32,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                anchor="w"
            )
            btn.pack(fill="x", pady=2)
            self.type_buttons[type_name] = btn
    
    def select_type(self, type_name):
        """选中一个类型并显示其配置"""
        # 先保存当前编辑
        if self.current_type:
            self.save_current_type()
        
        self.current_type = type_name
        
        # 更新按钮样式
        for name, btn in self.type_buttons.items():
            if name == type_name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color="transparent")
        
        # 更新名称输入框
        self.type_name_entry.delete(0, "end")
        self.type_name_entry.insert(0, type_name)
        
        # 更新子文件夹文本
        subfolders = self.config["subfolder_config"].get(type_name, {})
        text = self.dict_to_text(subfolders)
        self.subfolder_text.delete("1.0", "end")
        self.subfolder_text.insert("1.0", text)
    
    def dict_to_text(self, folder_dict, indent=0):
        """将文件夹字典转换为缩进文本"""
        lines = []
        for name, children in folder_dict.items():
            lines.append("  " * indent + name)
            if children:
                lines.append(self.dict_to_text(children, indent + 1))
        return "\n".join(lines)
    
    def text_to_dict(self, text):
        """将缩进文本转换为文件夹字典"""
        lines = text.strip().split("\n")
        if not lines or lines == ['']:
            return {}
        
        result = {}
        stack = [(result, -1)]  # (当前字典, 缩进级别)
        
        for line in lines:
            # 跳过空行
            if not line.strip():
                continue
            
            # 计算缩进级别（支持空格和Tab）
            original_len = len(line)
            stripped = line.lstrip(' \t')
            leading_space = original_len - len(stripped)
            
            # 将Tab视为2空格，然后计算缩进级别
            indent = leading_space // 2
            name = stripped.strip()
            
            if not name:
                continue
            
            # 找到父级 - 确保栈不会变空
            while len(stack) > 1 and stack[-1][1] >= indent:
                stack.pop()
            
            # 添加到父级字典
            parent_dict = stack[-1][0]
            parent_dict[name] = {}
            stack.append((parent_dict[name], indent))
        
        return result
    
    def save_current_type(self):
        """保存当前正在编辑的类型"""
        if not self.current_type:
            return
        
        text = self.subfolder_text.get("1.0", "end")
        folder_dict = self.text_to_dict(text)
        self.config["subfolder_config"][self.current_type] = folder_dict
    
    def add_new_type(self):
        """添加新类型"""
        # 弹出输入对话框
        dialog = ctk.CTkInputDialog(text="输入新类型名称:", title="新建模板")
        new_name = dialog.get_input()
        
        if new_name:
            new_name = new_name.strip().upper()
            if new_name in self.config["subfolder_config"]:
                messagebox.showwarning("提示", f"类型 '{new_name}' 已存在！")
                return
            
            self.config["subfolder_config"][new_name] = {}
            self.refresh_type_list()
            self.select_type(new_name)
    
    def delete_type(self):
        """删除当前类型"""
        if not self.current_type:
            return
        
        if len(self.config["subfolder_config"]) <= 1:
            messagebox.showwarning("提示", "至少保留一个类型！")
            return
        
        if messagebox.askyesno("确认删除", f"确定删除类型 '{self.current_type}'？"):
            del self.config["subfolder_config"][self.current_type]
            self.current_type = None
            self.refresh_type_list()
            
            # 选中第一个
            if self.config["subfolder_config"]:
                first_type = list(self.config["subfolder_config"].keys())[0]
                self.select_type(first_type)
    
    def rename_type(self):
        """重命名当前类型"""
        if not self.current_type:
            return
        
        new_name = self.type_name_entry.get().strip().upper()
        if not new_name:
            messagebox.showwarning("提示", "名称不能为空！")
            return
        
        if new_name == self.current_type:
            return
        
        if new_name in self.config["subfolder_config"]:
            messagebox.showwarning("提示", f"类型 '{new_name}' 已存在！")
            return
        
        # 重命名
        old_data = self.config["subfolder_config"][self.current_type]
        del self.config["subfolder_config"][self.current_type]
        self.config["subfolder_config"][new_name] = old_data
        
        self.current_type = new_name
        self.refresh_type_list()
        self.select_type(new_name)
    
    def browse_default_path(self):
        """浏览默认路径"""
        folder = filedialog.askdirectory(
            initialdir=self.default_path_entry.get(),
            title="选择默认路径"
        )
        if folder:
            self.default_path_entry.delete(0, "end")
            self.default_path_entry.insert(0, folder)
    
    def save_all(self):
        """保存所有配置"""
        # 保存当前编辑的类型
        self.save_current_type()
        
        # 保存默认路径
        self.config["default_path"] = self.default_path_entry.get().strip()
        
        # 写入文件
        save_config(self.config)
        
        # 回调通知主窗口刷新
        if self.on_save_callback:
            self.on_save_callback()
        
        messagebox.showinfo("成功", "配置已保存！")
        self.destroy()


# ============================================================
# 主应用类
# ============================================================

class ProjectTemplateBuilder(ctk.CTk):
    """项目模板构建器主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 加载配置
        self.reload_config()
        
        # 窗口基本设置
        self.title("📁 项目模板构建器")
        self.geometry("500x360")
        self.resizable(False, False)
        
        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 窗口置顶
        self.attributes("-topmost", True)
        
        # 居中显示
        self.center_window()
        
        # 创建界面
        self.create_widgets()
        
        # 绑定回车键
        self.bind("<Return>", lambda e: self.create_and_exit())
    
    def reload_config(self):
        """重新加载配置"""
        global CONFIG
        CONFIG = load_config()
        self.subfolder_config = CONFIG.get("subfolder_config", {})
        self.project_types = list(self.subfolder_config.keys())
        self.default_path = CONFIG.get("default_path", r"D:\00working")
    
    def center_window(self):
        """将窗口居中显示"""
        self.update_idletasks()
        width = 500
        height = 360
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """创建界面控件"""
        
        # 主容器
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=25)
        
        # 顶部：标题 + 设置按钮
        top_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ctk.CTkLabel(
            top_frame, 
            text="🚀 快速创建项目文件夹",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left")
        
        settings_btn = ctk.CTkButton(
            top_frame,
            text="⚙️ 设置",
            width=80,
            height=32,
            command=self.open_settings,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30")
        )
        settings_btn.pack(side="right")
        
        # ---- Type 下拉菜单 ----
        type_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        type_frame.pack(fill="x", pady=8)
        
        type_label = ctk.CTkLabel(
            type_frame, 
            text="Type（类型）:",
            font=ctk.CTkFont(size=14),
            width=100,
            anchor="w"
        )
        type_label.pack(side="left")
        
        self.type_var = ctk.StringVar(value=self.project_types[0] if self.project_types else "")
        self.type_dropdown = ctk.CTkComboBox(
            type_frame,
            values=self.project_types,
            variable=self.type_var,
            width=280,
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=13),
            state="readonly"
        )
        self.type_dropdown.pack(side="right", fill="x", expand=True)
        
        # ---- Detail 输入框 ----
        detail_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        detail_frame.pack(fill="x", pady=8)
        
        detail_label = ctk.CTkLabel(
            detail_frame, 
            text="Detail（详情）:",
            font=ctk.CTkFont(size=14),
            width=100,
            anchor="w"
        )
        detail_label.pack(side="left")
        
        self.detail_entry = ctk.CTkEntry(
            detail_frame,
            placeholder_text="输入项目名称...",
            width=280,
            font=ctk.CTkFont(size=13)
        )
        self.detail_entry.pack(side="right", fill="x", expand=True)
        self.detail_entry.focus()
        
        # ---- Path 路径选择 ----
        path_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        path_frame.pack(fill="x", pady=8)
        
        path_label = ctk.CTkLabel(
            path_frame, 
            text="Path（路径）:",
            font=ctk.CTkFont(size=14),
            width=100,
            anchor="w"
        )
        path_label.pack(side="left")
        
        self.path_var = ctk.StringVar(value=self.default_path)
        self.path_entry = ctk.CTkEntry(
            path_frame,
            textvariable=self.path_var,
            width=200,
            font=ctk.CTkFont(size=12)
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        browse_btn = ctk.CTkButton(
            path_frame,
            text="浏览",
            width=70,
            command=self.browse_path,
            font=ctk.CTkFont(size=13)
        )
        browse_btn.pack(side="right")
        
        # ---- 创建按钮 ----
        self.create_btn = ctk.CTkButton(
            main_frame,
            text="✨ Create & Exit",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.create_and_exit,
            fg_color="#2563eb",
            hover_color="#1d4ed8"
        )
        self.create_btn.pack(fill="x", pady=(25, 0))
    
    def open_settings(self):
        """打开设置窗口"""
        TemplateManagerWindow(self, on_save_callback=self.on_config_saved)
    
    def on_config_saved(self):
        """配置保存后的回调"""
        self.reload_config()
        # 更新下拉菜单
        self.type_dropdown.configure(values=self.project_types)
        if self.project_types:
            self.type_var.set(self.project_types[0])
        # 更新默认路径
        self.path_var.set(self.default_path)
    
    def browse_path(self):
        """打开文件夹选择对话框"""
        folder = filedialog.askdirectory(
            initialdir=self.path_var.get(),
            title="选择目标路径"
        )
        if folder:
            self.path_var.set(folder)
    
    def create_folders_recursive(self, base_path, folder_dict):
        """递归创建文件夹结构"""
        for name, children in folder_dict.items():
            folder_path = os.path.join(base_path, name)
            os.makedirs(folder_path, exist_ok=True)
            if children:
                self.create_folders_recursive(folder_path, children)
    
    def create_and_exit(self):
        """创建文件夹并退出程序"""
        
        # 获取输入值
        project_type = self.type_var.get().strip()
        detail = self.detail_entry.get().strip()
        base_path = self.path_var.get().strip()
        
        # 验证输入
        if not detail:
            messagebox.showwarning("⚠️ 提示", "请输入项目详情 (Detail)！")
            self.detail_entry.focus()
            return
        
        if not os.path.exists(base_path):
            messagebox.showerror("❌ 错误", f"路径不存在：\n{base_path}")
            return
        
        # 生成文件夹名称：YYYYMMDD_TYPE_DETAIL
        date_str = datetime.now().strftime("%Y%m%d")
        folder_name = f"{date_str}_{project_type}_{detail}"
        full_path = os.path.join(base_path, folder_name)
        
        # 检查是否已存在
        if os.path.exists(full_path):
            messagebox.showerror("❌ 错误", f"文件夹已存在：\n{folder_name}")
            return
        
        try:
            # 创建父文件夹
            os.makedirs(full_path)
            
            # 创建子文件夹（支持多级）
            subfolders = self.subfolder_config.get(project_type, {})
            self.create_folders_recursive(full_path, subfolders)
            
            # 显示成功提示（0.5秒后自动关闭）
            self.show_success_and_exit(folder_name)
            
        except Exception as e:
            messagebox.showerror("❌ 创建失败", f"发生错误：\n{str(e)}")
    
    def show_success_and_exit(self, folder_name: str):
        """显示成功提示窗口，0.5秒后自动关闭并退出程序"""
        
        success_window = ctk.CTkToplevel(self)
        success_window.title("✅ 成功")
        success_window.geometry("350x120")
        success_window.resizable(False, False)
        success_window.attributes("-topmost", True)
        success_window.grab_set()
        
        # 居中显示
        success_window.update_idletasks()
        x = (success_window.winfo_screenwidth() // 2) - (175)
        y = (success_window.winfo_screenheight() // 2) - (60)
        success_window.geometry(f"350x120+{x}+{y}")
        
        msg_label = ctk.CTkLabel(
            success_window,
            text=f"✅ 创建成功！\n\n📁 {folder_name}",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        msg_label.pack(expand=True, pady=20)
        
        success_window.after(500, self.exit_app)
    
    def exit_app(self):
        """彻底退出程序"""
        self.quit()
        self.destroy()
        sys.exit(0)


# ============================================================
# 程序入口
# ============================================================

if __name__ == "__main__":
    app = ProjectTemplateBuilder()
    app.mainloop()

