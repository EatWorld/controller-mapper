import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pygame
import pyautogui
import mouse
import json
import os
import time
import threading
from typing import Dict, Any, Optional

__version__ = "1.1.0"

# 优化PyAutoGUI的性能（保留用于其他功能）
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.PAUSE = 0

# 导入Windows API相关模块
import ctypes
from ctypes import wintypes
import win32con
import math

# python-ds4项目的鼠标移动实现
from collections import defaultdict

class MouseMotion:
    """
    基于python-ds4项目的鼠标移动实现
    使用mouse库进行鼠标控制，更加稳定可靠
    """

    def __init__(self, state: dict):
        self.state: dict = state
        
        # python-ds4的参数设置
        self.left_axis_speed = 0.04   # 左摇杆速度（精细控制）
        self.right_axis_speed = 0.15  # 右摇杆速度（快速移动）
        self.axis_thr = 0.008         # 死区阈值
        
        # 轴值存储
        self.axis = defaultdict(lambda: 0)
        
        # 当前轴值（兼容接口）
        self.x_axis = 0.0
        self.y_axis = 0.0
        
        # 滚轮相关
        self.scroll_mode = False
        self.wheel_direction = 0
        
        # 启动移动线程
        threading.Thread(target=self.run, daemon=True).start()
    
    def main_loop_iteration(self):
        """python-ds4的主循环逻辑"""
        # 应用死区
        x_val = self.x_axis if abs(self.x_axis) > self.axis_thr else 0
        y_val = self.y_axis if abs(self.y_axis) > self.axis_thr else 0
        
        # 计算移动量（使用右摇杆速度）
        axis0 = x_val * self.right_axis_speed
        axis1 = y_val * self.right_axis_speed
        
        if abs(axis0) > 0 or abs(axis1) > 0:
            if self.scroll_mode and self.wheel_direction != 0:
                # 滚轮模式
                mouse.wheel(self.wheel_direction)
            else:
                # 鼠标移动模式
                mouse.move(axis0 * 100, axis1 * 100, absolute=False)

    def run(self):
        """主运行循环"""
        while self.state['alive']:
            if self.state.get('sleep', False):
                time.sleep(0.1)
                continue
                
            # 执行鼠标控制逻辑
            self.main_loop_iteration()
            
            # 60Hz更新频率（与python-ds4一致）
            time.sleep(1/60)
    
    # 兼容接口
    def start(self):
        """启动鼠标移动线程（自动启动）"""
        print("鼠标移动线程已启动（python-ds4版本）")
    
    def stop(self):
        """停止鼠标移动线程"""
        self.state['alive'] = False
        print("鼠标移动线程已停止")
    
    def set_velocity(self, x_axis: float, y_axis: float):
        """设置轴值"""
        self.x_axis = x_axis
        self.y_axis = y_axis
        
    def set_multiplier(self, multiplier: float):
        """设置速度倍率（调整右摇杆速度）"""
        self.right_axis_speed = 0.15 * multiplier
        
    def set_wheel_direction(self, direction: int):
        """设置滚轮方向"""
        self.wheel_direction = direction
        self.scroll_mode = direction != 0

class StyleManager:
    """样式管理器 - 统一管理界面样式"""
    
    def __init__(self, style: ttk.Style):
        self.style = style
        
    def apply_modern_theme(self):
        """应用macOS风格主题"""
        # 设置基础主题
        self.style.theme_use('default')
        
        # 全局字体设置 - 隶书风格
        default_font = ('隶书', 12) if self._font_exists('隶书') else ('LiSu', 12) if self._font_exists('LiSu') else ('Microsoft YaHei UI', 12)
        title_font = ('隶书', 22, 'bold') if self._font_exists('隶书') else ('LiSu', 22, 'bold') if self._font_exists('LiSu') else ('Microsoft YaHei UI', 22, 'bold')
        
        # 现代化柔和配色方案
        colors = {
            'bg_primary': '#FAFAFA',      # 主背景色 - 极浅灰白
            'bg_secondary': '#FFFFFF',     # 次要背景色 - 纯白
            'bg_card': '#FFFFFF',         # 卡片背景色 - 纯白
            'bg_sidebar': '#F8F9FA',      # 侧边栏背景
            'text_primary': '#2C3E50',     # 主文字色 - 深蓝灰
            'text_secondary': '#6C757D',   # 次要文字色 - 中灰
            'text_tertiary': '#ADB5BD',    # 三级文字色 - 浅灰
            'border': '#E9ECEF',          # 边框色 - 极浅灰
            'separator': '#DEE2E6',       # 分隔线色
            'focus': '#4A90E2',           # 焦点色 - 柔和蓝
            'success': '#28A745',         # 成功色 - 柔和绿
            'warning': '#FFC107',         # 警告色 - 柔和橙
            'danger': '#DC3545',          # 危险色 - 柔和红
            'accent_blue': '#4A90E2',     # 蓝色强调
            'accent_purple': '#6F42C1',   # 紫色强调
            'accent_teal': '#20C997',     # 青色强调
            'shadow': 'rgba(0,0,0,0.08)'  # 阴影色
        }
        
        # 存储颜色配置供其他方法使用
        self.colors = colors
        self.default_font = default_font
        self.title_font = title_font
        
        # 应用所有样式
        self._configure_frames()
        self._configure_labels()
        self._configure_entries()
        self._configure_comboboxes()
        self._configure_buttons()
        self._configure_labelframes()
    
    def _font_exists(self, font_name):
        """检查字体是否存在"""
        try:
            import tkinter.font as tkFont
            return font_name in tkFont.families()
        except:
            return False
    
    def _configure_frames(self):
        """配置框架样式"""
        # 主框架样式 - 现代浅色背景
        self.style.configure('Main.TFrame', 
                           background=self.colors['bg_primary'])
        
        # 卡片框架样式 - 白色卡片背景
        self.style.configure('Card.TFrame',
                           background=self.colors['bg_card'],
                           relief='flat')
        
        # 按键配置框架样式 - 卡片式设计
        self.style.configure('ButtonConfig.TFrame',
                           background=self.colors['bg_card'],
                           relief='flat')
        
        # 状态区域框架
        self.style.configure('Status.TFrame',
                           background=self.colors['bg_card'],
                           relief='flat')
        
        # 控制区域框架
        self.style.configure('Control.TFrame',
                           background=self.colors['bg_primary'],
                           relief='flat')
    
    def _configure_labels(self):
        """配置标签样式"""
        # 主标签样式
        self.style.configure('Primary.TLabel',
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_primary'],
                           font=self.default_font)
        
        # 次要标签样式
        self.style.configure('Secondary.TLabel',
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_secondary'],
                           font=(self.default_font[0], 10))
        
        # 标题样式 - macOS大标题
        self.style.configure('Title.TLabel',
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_primary'],
                           font=self.title_font)
        
        # 副标题样式
        self.style.configure('Subtitle.TLabel',
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_secondary'],
                           font=(self.default_font[0], 14))
        
        # 手柄状态样式
        self.style.configure('Status.TLabel',
                           background=self.colors['bg_primary'],
                           foreground=self.colors['success'],
                           font=(self.default_font[0], 13, 'bold'))
        
        self.style.configure('StatusDisconnected.TLabel',
                           background=self.colors['bg_primary'],
                           foreground=self.colors['danger'],
                           font=(self.default_font[0], 13, 'bold'))
    
    def _configure_labelframes(self):
        """配置标签框架样式 - 现代卡片风格"""
        self.style.configure('Config.TLabelframe',
                           background=self.colors['bg_card'],
                           relief='solid',
                           borderwidth=1,
                           bordercolor=self.colors['border'],
                           lightcolor=self.colors['bg_card'],
                           darkcolor=self.colors['bg_card'])
        
        self.style.configure('Config.TLabelframe.Label',
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_primary'],
                           font=(self.default_font[0], 12, 'bold'))
        
        # 状态信息框架
        self.style.configure('StatusInfo.TLabelframe',
                           background=self.colors['bg_card'],
                           relief='flat',
                           borderwidth=0)
        
        self.style.configure('StatusInfo.TLabelframe.Label',
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_secondary'],
                           font=(self.default_font[0], 10))
        
    def _configure_entries(self):
        """配置输入框样式 - macOS风格"""
        self.style.configure('Modern.TEntry',
                           fieldbackground=self.colors['bg_secondary'],
                           borderwidth=1,
                           relief='solid',
                           bordercolor=self.colors['border'],
                           insertcolor=self.colors['focus'],
                           foreground=self.colors['text_primary'],
                           padding=(12, 8))
        
        self.style.map('Modern.TEntry',
                      bordercolor=[('focus', self.colors['focus']),
                                 ('active', self.colors['focus'])],
                      fieldbackground=[('focus', self.colors['bg_secondary'])])
    
    def _configure_comboboxes(self):
        """配置下拉框样式 - macOS风格"""
        self.style.configure('Modern.TCombobox',
                           fieldbackground=self.colors['bg_secondary'],
                           borderwidth=1,
                           relief='solid',
                           bordercolor=self.colors['border'],
                           arrowcolor=self.colors['text_secondary'],
                           foreground=self.colors['text_primary'],
                           padding=(12, 8))
        
        self.style.map('Modern.TCombobox',
                      bordercolor=[('focus', self.colors['focus']),
                                 ('active', self.colors['focus'])],
                      fieldbackground=[('readonly', self.colors['bg_secondary']),
                                     ('focus', self.colors['bg_secondary'])],
                      arrowcolor=[('active', self.colors['focus'])])
        
    def _configure_buttons(self):
        """配置按钮样式 - macOS风格"""
        # 主要按钮 - 现代蓝色
        self.style.configure('Primary.TButton',
                           background=self.colors['focus'],
                           foreground='white',
                           borderwidth=0,
                           relief='flat',
                           font=(self.default_font[0], 12, 'bold'),
                           padding=(20, 12))
        
        self.style.map('Primary.TButton',
                      background=[('active', '#357ABD'),
                                ('pressed', '#2E6DA4')])
        
        # 次要按钮 - 现代边框
        self.style.configure('Secondary.TButton',
                           background=self.colors['bg_secondary'],
                           foreground=self.colors['text_primary'],
                           borderwidth=1,
                           relief='solid',
                           bordercolor=self.colors['border'],
                           font=(self.default_font[0], 11),
                           padding=(18, 10))
        
        self.style.map('Secondary.TButton',
                      background=[('active', '#F8F9FA'),
                                ('pressed', '#E9ECEF')],
                      bordercolor=[('active', self.colors['focus'])])
        
        # 成功按钮 - 现代绿色
        self.style.configure('Success.TButton',
                           background=self.colors['success'],
                           foreground='white',
                           borderwidth=0,
                           relief='flat',
                           font=(self.default_font[0], 12, 'bold'),
                           padding=(20, 12))
        
        self.style.map('Success.TButton',
                      background=[('active', '#218838'),
                                ('pressed', '#1E7E34')])
        
        # 危险按钮 - 现代红色
        self.style.configure('Danger.TButton',
                           background=self.colors['danger'],
                           foreground='white',
                           borderwidth=0,
                           relief='flat',
                           font=(self.default_font[0], 12, 'bold'),
                           padding=(20, 12))
        
        self.style.map('Danger.TButton',
                      background=[('active', '#C82333'),
                                ('pressed', '#BD2130')])
        
        # 小型按钮 - 用于文件操作
        self.style.configure('Small.TButton',
                           background=self.colors['bg_secondary'],
                           foreground=self.colors['text_primary'],
                           borderwidth=1,
                           relief='solid',
                           bordercolor=self.colors['border'],
                           font=(self.default_font[0], 10),
                           padding=(12, 8))
        
        self.style.map('Small.TButton',
                      background=[('active', '#F8F9FA'),
                                ('pressed', '#E9ECEF')],
                      bordercolor=[('active', self.colors['focus'])])

class ConfigManager:
    """配置管理器 - 处理配置文件的保存和加载"""
    
    def __init__(self, default_filename: str = "xbox_config.json"):
        self.default_filename = default_filename
        
    def save_config(self, config: Dict[str, Any], filename: str = None) -> bool:
        """保存配置到文件"""
        try:
            if filename is None:
                filename = self.default_filename
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def load_config(self, filename: str = None) -> Dict[str, Any]:
        """从文件加载配置"""
        try:
            if filename is None:
                filename = self.default_filename
            
            if not os.path.exists(filename):
                return {}
            
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}
    
    def get_config_files(self) -> list:
        """获取当前目录下的所有配置文件"""
        try:
            files = [f for f in os.listdir('.') if f.endswith('.json')]
            return files
        except:
            return []

class ControllerHandler:
    """手柄处理器 - 管理手柄连接和输入检测"""

    # 轴布局预设：根据总轴数自动选择最匹配的布局
    # 格式: (left_x, left_y, lt, right_x, right_y, rt)
    AXIS_LAYOUTS = {
        6: (0, 1, 2, 3, 4, 5),       # 标准Xbox布局（SDL/XInput）
        5: (0, 1, None, 2, 3, 4),    # 无独立LT轴的布局
        4: (0, 1, None, 2, 3, None), # 只有摇杆轴
    }

    def __init__(self):
        self.joystick = None
        self.is_connected = False
        self.button_states = {}
        self._axis_layout = None  # 检测到的轴布局
        self._trigger_baseline = {}  # 扳机键静止基准值

    def initialize(self) -> bool:
        """初始化手柄"""
        try:
            pygame.init()
            pygame.joystick.init()

            if pygame.joystick.get_count() == 0:
                return False

            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.is_connected = True

            # 自动检测轴布局
            self._detect_axis_layout()

            print(f"手柄已连接: {self.joystick.get_name()}")
            return True
        except Exception as e:
            print(f"手柄初始化失败: {e}")
            return False

    def _detect_axis_layout(self):
        """自动检测手柄轴布局"""
        if not self.joystick:
            return

        num_axes = self.joystick.get_numaxes()
        name = self.joystick.get_name().lower()

        # 先按轴数匹配预设
        if num_axes in self.AXIS_LAYOUTS:
            layout = self.AXIS_LAYOUTS[num_axes]
        else:
            # 轴数不在预设中，用通用方案：前两个是左摇杆，后面的按位置推断
            if num_axes >= 6:
                layout = (0, 1, 2, 3, 4, 5)
            elif num_axes >= 4:
                layout = (0, 1, None, 2, 3, None)
            else:
                layout = (0, 1, None, None, None, None)

        self._axis_layout = {
            "left_x": layout[0],
            "left_y": layout[1],
            "lt": layout[2],
            "right_x": layout[3],
            "right_y": layout[4],
            "rt": layout[5],
        }

        # 采样静止状态基准值（用于扳机键零点校准）
        pygame.event.pump()
        self._trigger_baseline = {}
        for key in ("lt", "rt"):
            idx = self._axis_layout.get(key)
            if idx is not None and idx < num_axes:
                self._trigger_baseline[key] = self.joystick.get_axis(idx)

        print(f"轴布局检测: 共{num_axes}轴, 布局={self._axis_layout}")
        if self._trigger_baseline:
            print(f"扳机基准值: {self._trigger_baseline}")

    def get_button_states(self) -> Dict[str, bool]:
        """获取当前按键状态"""
        if not self.is_connected or not self.joystick:
            return {}

        try:
            pygame.event.pump()

            if not self.joystick.get_init():
                self.is_connected = False
                return {}

            states = {
                "A": bool(self.joystick.get_button(0)),
                "B": bool(self.joystick.get_button(1)),
                "X": bool(self.joystick.get_button(2)),
                "Y": bool(self.joystick.get_button(3)),
                "LB": bool(self.joystick.get_button(4)),
                "RB": bool(self.joystick.get_button(5)),
            }

            # 扳机键检测（使用自动检测的轴布局）
            try:
                num_axes = self.joystick.get_numaxes()
                for trigger_name in ("LT", "RT"):
                    key = trigger_name.lower()
                    idx = self._axis_layout.get(key) if self._axis_layout else None
                    if idx is not None and idx < num_axes:
                        raw = self.joystick.get_axis(idx)
                        # 如果有基准值，做零点偏移校准
                        baseline = self._trigger_baseline.get(key, -1.0)
                        if baseline > 0.5:
                            # 基准值在正半轴（如SDL布局，静止=-1），标准化: (raw - baseline) 归零
                            # 正常情况基准约 -1.0，按下去趋向 +1.0
                            pass
                        # 标准化: 将 -1~+1 映射为 0~1
                        normalized = (raw + 1) / 2
                        # 扣除基准偏移（防止静止时漂移触发）
                        baseline_norm = (baseline + 1) / 2
                        effective = max(0, normalized - baseline_norm)
                        # 保留小量余量防止误触
                        states[trigger_name] = effective > 0.08
                    else:
                        states[trigger_name] = False
            except Exception as e:
                print(f"扳机键检测异常: {e}")
                states["LT"] = False
                states["RT"] = False

            pressed_buttons = [name for name, pressed in states.items() if pressed]
            if pressed_buttons:
                print(f"检测到按键: {pressed_buttons}")

            return states
        except Exception as e:
            print(f"获取按键状态失败: {e}")
            self.is_connected = False
            return {}

    def get_joystick_axes(self) -> Dict[str, tuple]:
        """获取摇杆轴状态"""
        if not self.is_connected or not self.joystick:
            return {}

        try:
            pygame.event.pump()

            if not self.joystick.get_init():
                self.is_connected = False
                return {}

            num_axes = self.joystick.get_numaxes()
            layout = self._axis_layout or {}

            def safe_axis(key):
                idx = layout.get(key)
                if idx is not None and idx < num_axes:
                    return self.joystick.get_axis(idx)
                return 0.0

            left_x = safe_axis("left_x")
            left_y = safe_axis("left_y")
            right_x = safe_axis("right_x")
            right_y = safe_axis("right_y")

            return {
                "left": (left_x, left_y),
                "right": (right_x, right_y)
            }
        except Exception as e:
            print(f"获取摇杆状态失败: {e}")
            self.is_connected = False
            return {}

    def reconnect(self) -> bool:
        """重新连接手柄"""
        self.is_connected = False
        return self.initialize()

class XboxControllerMapperGUI:
    """Xbox手柄映射工具主界面"""
    
    def __init__(self, master):
        self.master = master
        self.setup_window()
        
        # 初始化管理器
        self.style_manager = StyleManager(ttk.Style())
        self.config_manager = ConfigManager()
        self.controller = ControllerHandler()
        
        # 创建GPad风格的state字典
        self.state = {'alive': True, 'sleep': False}
        self.mouse_motion = MouseMotion(self.state)
        
        # 应用样式
        self.style_manager.apply_modern_theme()
        
        # 设置窗口背景色
        self.master.configure(bg=self.style_manager.colors['bg_primary'])
        
        # 尝试初始化手柄（允许失败）
        self.controller.initialize()
        
        # 按键映射配置
        self.button_mappings = self.create_default_mappings()
        
        # 摇杆映射配置
        self.joystick_mouse_enabled = tk.BooleanVar(value=True)  # 默认开启
        self.joystick_selection = tk.StringVar(value="右摇杆")  # 默认右摇杆
        
        # 界面变量
        self.mouse_coords_var = tk.StringVar(value="鼠标位置: X=0, Y=0")
        self.status_var = tk.StringVar(value="就绪")
        self.running = False
        
        # 按键防抖动状态
        self.last_button_states = {}
        
        # 创建界面
        self.create_widgets()
        
        # 加载配置
        self.load_configuration()
        
        # 绑定事件
        self.bind_events()
        
        # 启动手柄状态检测
        self.start_controller_detection()
        
        # 启动主循环
        self.start_main_loop()
        
        # 延迟自动启动映射功能，确保UI完全初始化
        self.master.after(500, self.auto_start_mapping)
    
    def setup_window(self):
        """设置窗口属性"""
        self.master.title("Xbox 手柄映射工具")
        self.master.geometry("1000x800")  # 减少窗口高度，去除多余空白
        self.master.resizable(False, False)  # 固定窗口大小
        
        # 居中显示窗口
        self.center_window()
        
        # 设置窗口图标（如果有的话）
        try:
            self.master.iconbitmap("icon.ico")
        except:
            pass
    
    def center_window(self):
        """将窗口居中显示"""
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_default_mappings(self) -> Dict[str, Dict[str, Any]]:
        """创建默认按键映射配置"""
        buttons = ["Y", "X", "B", "A", "RT", "LT", "RB", "LB"]
        mappings = {}
        
        for button in buttons:
            mappings[button] = {
                "action_type": "无动作",
                "mouse_x": "",
                "mouse_y": "",
                "keyboard_key": "",
                "action_type_var": tk.StringVar(value="无动作")
            }
        
        return mappings
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.master, style='Main.TFrame')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # 顶部区域 - 标题和状态
        self.create_header(main_frame)
        
        # 配置区域
        self.create_config_area(main_frame)
        
        # 底部区域 - 状态和控制
        self.create_footer(main_frame)
    
    def create_header(self, parent):
        """创建顶部标题和状态区域"""
        header_frame = ttk.Frame(parent, style='Main.TFrame')
        header_frame.pack(fill='x', pady=(0, 15))
        
        # 标题区域
        title_container = ttk.Frame(header_frame, style='Main.TFrame')
        title_container.pack(fill='x')
        
        title_label = ttk.Label(title_container, 
                               text="Xbox 手柄映射工具",
                               style='Title.TLabel')
        title_label.pack()
        
        # 删除副标题以节省空间
        
        # 移除顶部的手柄状态显示
    
    def create_config_area(self, parent):
        """创建配置区域"""
        # 配置容器 - 卡片式设计
        config_container = ttk.Frame(parent, style='Card.TFrame')
        config_container.pack(fill='both', expand=True, pady=(0, 15))
        
        # 移除配置标题以节省空间
        
        # 按键配置网格
        self.create_button_configs(config_container)
        
        # 摇杆映射和鼠标位置水平布局容器
        horizontal_container = ttk.Frame(config_container, style='Card.TFrame')
        horizontal_container.pack(fill='x', padx=15, pady=(0, 5))  # 进一步减少间距
        
        # 摇杆映射配置 - 左侧
        self.create_joystick_config(horizontal_container, side='left')
        
        # 鼠标坐标显示和操作提示 - 右侧
        self.create_mouse_display(horizontal_container, side='right')
    
    def create_button_configs(self, parent):
        """创建按键配置区域 - 现代卡片式布局"""
        # 按键配置容器
        configs_container = ttk.Frame(parent, style='Card.TFrame')
        configs_container.pack(fill='x', padx=15, pady=(0, 15))
        
        # 按键分组 - 模拟手柄布局
        button_groups = [
            {"title": "面部按键", "buttons": ["Y", "X", "B", "A"]},
            {"title": "肩部按键", "buttons": ["LB", "RB", "LT", "RT"]}
        ]
        
        for group_idx, group in enumerate(button_groups):
            # 分组标题
            group_title = ttk.Label(configs_container,
                                   text=group["title"],
                                   style='Secondary.TLabel',
                                   font=(self.style_manager.default_font[0], 12, 'bold'))
            group_title.grid(row=group_idx*2, column=0, columnspan=4, 
                           sticky='w', pady=(15 if group_idx > 0 else 0, 8))
            
            # 按键配置
            for i, button_name in enumerate(group["buttons"]):
                col = i
                row = group_idx*2 + 1
                
                # 按键配置卡片
                config_frame = ttk.LabelFrame(configs_container, 
                                            text=f"按键 {button_name}",
                                            style='Config.TLabelframe')
                config_frame.grid(row=row, column=col, 
                                sticky='ew', padx=6, pady=4)
                
                # 配置网格权重
                configs_container.grid_columnconfigure(col, weight=1)
                config_frame.grid_columnconfigure(1, weight=1)
                
                self.create_button_config_widgets(config_frame, button_name)
    
    def create_button_config_widgets(self, parent, button_name):
        """创建单个按键的配置组件 - 现代卡片风格"""
        mapping = self.button_mappings[button_name]
        
        # 动作类型选择
        ttk.Label(parent, text="动作类型", style='Primary.TLabel').grid(
            row=0, column=0, sticky='w', padx=10, pady=6)
        
        action_combo = ttk.Combobox(parent,
                                  textvariable=mapping["action_type_var"],
                                  values=["无动作", "鼠标点击", "键盘按键"],
                                  style='Modern.TCombobox',
                                  state='readonly')
        action_combo.grid(row=0, column=1, sticky='ew', padx=10, pady=6)
        action_combo.bind('<<ComboboxSelected>>', 
                         lambda e, btn=button_name: self.on_action_type_changed(btn))
        
        # 鼠标坐标输入（初始隐藏）
        mouse_frame = ttk.Frame(parent, style='ButtonConfig.TFrame')
        mouse_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=10, pady=4)
        mouse_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(mouse_frame, text="坐标(X,Y)", style='Primary.TLabel').grid(
            row=0, column=0, sticky='w', padx=(0, 6))
        
        mouse_entry = ttk.Entry(mouse_frame, style='Modern.TEntry')
        mouse_entry.grid(row=0, column=1, sticky='ew')
        mouse_entry.bind('<FocusOut>', 
                        lambda e, btn=button_name: self.update_mouse_config(btn))
        
        mapping["mouse_frame"] = mouse_frame
        mapping["mouse_entry"] = mouse_entry
        mouse_frame.grid_remove()
        
        # 键盘按键输入（初始隐藏）
        keyboard_frame = ttk.Frame(parent, style='ButtonConfig.TFrame')
        keyboard_frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=8, pady=2)
        keyboard_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(keyboard_frame, text="按键", style='Primary.TLabel').grid(
            row=0, column=0, sticky='w', padx=(0, 6))
        
        keyboard_entry = ttk.Entry(keyboard_frame, style='Modern.TEntry')
        keyboard_entry.grid(row=0, column=1, sticky='ew')
        keyboard_entry.bind('<FocusOut>', 
                           lambda e, btn=button_name: self.update_keyboard_config(btn))
        
        mapping["keyboard_frame"] = keyboard_frame
        mapping["keyboard_entry"] = keyboard_entry
        keyboard_frame.grid_remove()
    
    def create_joystick_config(self, parent, side='top'):
        """创建摇杆映射配置区域"""
        joystick_container = ttk.LabelFrame(parent, 
                                           text="摇杆映射配置区域",
                                           style='Config.TLabelframe')
        if side == 'left':
            joystick_container.pack(side='left', fill='both', expand=True, padx=(0, 8))
        else:
            joystick_container.pack(fill='x', padx=15, pady=(0, 15))
        
        # 摇杆配置选项
        joystick_options_frame = ttk.Frame(joystick_container, style='Card.TFrame')
        joystick_options_frame.pack(fill='x', padx=10, pady=10)

        # 启用摇杆映射复选框
        enable_checkbox = ttk.Checkbutton(joystick_options_frame,
                                         text="启用摇杆映射为鼠标",
                                         variable=self.joystick_mouse_enabled)
        enable_checkbox.pack(anchor='w', pady=(0, 12))

        # 摇杆选择
        joystick_select_frame = ttk.Frame(joystick_options_frame, style='Card.TFrame')
        joystick_select_frame.pack(fill='x')

        ttk.Label(joystick_select_frame,
                 text="选择摇杆：",
                 style='Primary.TLabel').pack(anchor='w', pady=(0, 5))

        joystick_combo = ttk.Combobox(joystick_select_frame,
                                     textvariable=self.joystick_selection,
                                     values=["左摇杆", "右摇杆"],
                                     style='Modern.TCombobox',
                                     state='readonly',
                                     width=15)
        joystick_combo.pack(anchor='w')
    
    def create_mouse_display(self, parent, side='top'):
        """创建鼠标坐标显示和操作提示"""
        # 鼠标位置显示容器
        mouse_container = ttk.LabelFrame(parent, 
                                        text="实时鼠标位置区域",
                                        style='Config.TLabelframe')
        if side == 'right':
            mouse_container.pack(side='right', fill='both', expand=True, padx=(8, 0))
        else:
            mouse_container.pack(fill='x', padx=15, pady=(0, 10))
        
        # 鼠标位置显示内容
        mouse_content = ttk.Frame(mouse_container, style='Card.TFrame')
        mouse_content.pack(fill='x', padx=10, pady=10)  # 减少内边距
        
        # 鼠标位置显示
        self.mouse_coords_var = tk.StringVar(value="鼠标位置: X=0, Y=0")
        self.mouse_position_label = ttk.Label(mouse_content, 
                                             textvariable=self.mouse_coords_var,
                                             style='Primary.TLabel',
                                             font=(self.style_manager.default_font[0], 12))
        self.mouse_position_label.pack(pady=(0, 12))
        
        # 操作提示 - 简洁版本
        tip_title = ttk.Label(mouse_content,
                             text="💡 操作提示",
                             style='Secondary.TLabel',
                             font=(self.style_manager.default_font[0], 10, 'bold'))
        tip_title.pack(anchor='w', pady=(0, 8))
        
        tips = [
            "按 Ctrl 键可快速获取当前鼠标坐标",
            "建议先配置所有按键后再启动映射"
        ]
        
        for tip in tips:
            tip_label = ttk.Label(mouse_content, 
                                 text=f"• {tip}",
                                 style='Secondary.TLabel',
                                 font=(self.style_manager.default_font[0], 9))
            tip_label.pack(anchor='w', pady=1)
    
    def create_footer(self, parent):
        """创建底部状态和控制区域"""
        footer_frame = ttk.Frame(parent, style='Main.TFrame')
        footer_frame.pack(fill='x', pady=(0, 0))
        
        # 状态信息区域
        self.create_status_area(footer_frame)
        
        # 控制按钮区域
        self.create_control_area(footer_frame)
    
    def create_status_area(self, parent):
        """创建状态显示区域"""
        status_container = ttk.Frame(parent, style='Card.TFrame')
        status_container.pack(fill='x', pady=(0, 15))
        
        # 手柄状态显示 - 带彩色圆点
        controller_frame = ttk.Frame(status_container, style='Card.TFrame')
        controller_frame.pack(fill='x', pady=(10, 5))
        
        self.controller_status_var = tk.StringVar(value="手柄状态：检测中...")
        
        controller_status_frame = ttk.Frame(controller_frame, style='Card.TFrame')
        controller_status_frame.pack()
        
        # 创建Canvas来绘制真正的彩色圆点
        self.controller_dot_canvas = tk.Canvas(controller_status_frame, width=12, height=12, 
                                              highlightthickness=0, bg=self.style_manager.colors['bg_card'])
        self.controller_dot_canvas.pack(side='left', padx=(0, 8))
        # 初始绘制红色圆点
        self.draw_status_dot(False)
        
        self.controller_status_label = ttk.Label(controller_status_frame,
                                                textvariable=self.controller_status_var,
                                                style='Primary.TLabel',
                                                font=(self.style_manager.default_font[0], 10))
        self.controller_status_label.pack(side='left')
        
        # 配置状态显示
        self.status_var = tk.StringVar(value="已加载配置: 默认配置")
        self.status_label = ttk.Label(status_container, 
                                     textvariable=self.status_var,
                                     style='Primary.TLabel',
                                     font=(self.style_manager.default_font[0], 10))
        self.status_label.pack(pady=(5, 10))
    
    def create_control_area(self, parent):
        """创建控制按钮区域"""
        control_container = ttk.Frame(parent, style='Card.TFrame')
        control_container.pack(fill='x')
        
        # 控制区域内容
        control_content = ttk.Frame(control_container, style='Card.TFrame')
        control_content.pack(fill='x', padx=15, pady=15)
        
        # 文件操作按钮组 - 左侧
        file_frame = ttk.Frame(control_content, style='Card.TFrame')
        file_frame.pack(side='left', fill='x', expand=True)
        
        file_label = ttk.Label(file_frame,
                              text="配置管理",
                              style='Secondary.TLabel',
                              font=(self.style_manager.default_font[0], 10, 'bold'))
        file_label.pack(anchor='w', pady=(0, 8))
        
        file_buttons_frame = ttk.Frame(file_frame, style='Card.TFrame')
        file_buttons_frame.pack(anchor='w')
        
        ttk.Button(file_buttons_frame, text="保存配置", 
                  command=self.save_config,
                  style='Small.TButton').pack(side='left', padx=(0, 8))
        
        ttk.Button(file_buttons_frame, text="加载配置", 
                  command=self.load_config_dialog,
                  style='Small.TButton').pack(side='left', padx=(0, 8))
        
        ttk.Button(file_buttons_frame, text="另存为", 
                  command=self.save_config_as,
                  style='Small.TButton').pack(side='left')
        
        # 映射控制按钮组 - 右侧
        mapping_frame = ttk.Frame(control_content, style='Card.TFrame')
        mapping_frame.pack(side='right')
        
        mapping_label = ttk.Label(mapping_frame,
                                 text="映射控制",
                                 style='Secondary.TLabel',
                                 font=(self.style_manager.default_font[0], 10, 'bold'))
        mapping_label.pack(anchor='e', pady=(0, 8))
        
        mapping_buttons_frame = ttk.Frame(mapping_frame, style='Card.TFrame')
        mapping_buttons_frame.pack(anchor='e')
        
        self.start_button = ttk.Button(mapping_buttons_frame, text="启动映射", 
                                      command=self.start_mapping,
                                      style='Success.TButton')
        self.start_button.pack(side='left', padx=(0, 10))
        
        self.stop_button = ttk.Button(mapping_buttons_frame, text="停止映射", 
                                     command=self.stop_mapping,
                                     style='Danger.TButton',
                                     state='disabled')
        self.stop_button.pack(side='left')
    
    def bind_events(self):
        """绑定事件"""
        self.master.bind('<Control_L>', self.on_ctrl_pressed)
        self.master.bind('<Control_R>', self.on_ctrl_pressed)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def start_controller_detection(self):
        """启动手柄状态检测"""
        self.check_controller_status()
        # 每2秒检测一次手柄状态
        self.master.after(2000, self.start_controller_detection)
    
    def draw_status_dot(self, is_connected):
        """绘制状态指示圆点"""
        self.controller_dot_canvas.delete("all")
        color = "#007AFF" if is_connected else "#FF3B30"  # 蓝色或红色
        self.controller_dot_canvas.create_oval(2, 2, 10, 10, fill=color, outline=color)
    
    def check_controller_status(self):
        """检查手柄连接状态"""
        try:
            # 检查当前手柄状态，不重新初始化pygame
            import pygame
            
            if pygame.joystick.get_count() > 0:
                # 有手柄连接
                if not self.controller.is_connected:
                    # 只有在未连接时才重新初始化
                    joystick = pygame.joystick.Joystick(0)
                    joystick.init()
                    controller_name = joystick.get_name()
                    self.controller_status_var.set(f"手柄状态：已连接 - {controller_name}")
                    self.draw_status_dot(True)  # 蓝色圆点表示已连接
                    
                    # 更新控制器状态
                    self.controller.is_connected = True
                    self.controller.joystick = joystick
                    print(f"手柄重新连接: {controller_name}")
                else:
                    # 手柄已连接，检查是否仍然有效
                    if self.controller.joystick and self.controller.joystick.get_init():
                        # 手柄仍然有效，确保状态显示正确
                        controller_name = self.controller.joystick.get_name()
                        self.controller_status_var.set(f"手柄状态：已连接 - {controller_name}")
                        self.draw_status_dot(True)  # 蓝色圆点表示已连接
                    else:
                        # 手柄失效，重新初始化
                        joystick = pygame.joystick.Joystick(0)
                        joystick.init()
                        controller_name = joystick.get_name()
                        self.controller.joystick = joystick
                        self.controller_status_var.set(f"手柄状态：已连接 - {controller_name}")
                        self.draw_status_dot(True)  # 蓝色圆点表示已连接
                        print("手柄重新初始化")
            else:
                # 没有手柄连接
                if self.controller.is_connected:
                    self.controller_status_var.set("手柄状态：未连接")
                    self.draw_status_dot(False)  # 红色圆点表示未连接
                    self.controller.is_connected = False
                    self.controller.joystick = None
                    print("手柄断开连接")
                    
        except Exception as e:
            self.controller_status_var.set("手柄状态：检测失败")
            self.draw_status_dot(False)  # 红色圆点表示检测失败
            print(f"手柄状态检测失败: {e}")
    
    def on_action_type_changed(self, button_name):
        """动作类型改变事件"""
        mapping = self.button_mappings[button_name]
        action_type = mapping["action_type_var"].get()
        mapping["action_type"] = action_type
        
        # 显示/隐藏相应的配置区域
        if action_type == "鼠标点击":
            mapping["mouse_frame"].grid()
            mapping["keyboard_frame"].grid_remove()
        elif action_type == "键盘按键":
            mapping["mouse_frame"].grid_remove()
            mapping["keyboard_frame"].grid()
        else:
            mapping["mouse_frame"].grid_remove()
            mapping["keyboard_frame"].grid_remove()
    
    def update_mouse_config(self, button_name):
        """更新鼠标配置"""
        mapping = self.button_mappings[button_name]
        coord_text = mapping["mouse_entry"].get().strip()
        
        try:
            if ',' in coord_text:
                x, y = map(int, coord_text.split(','))
                mapping["mouse_x"] = str(x)
                mapping["mouse_y"] = str(y)
            else:
                mapping["mouse_x"] = ""
                mapping["mouse_y"] = ""
        except ValueError:
            mapping["mouse_x"] = ""
            mapping["mouse_y"] = ""
    
    def update_keyboard_config(self, button_name):
        """更新键盘配置"""
        mapping = self.button_mappings[button_name]
        mapping["keyboard_key"] = mapping["keyboard_entry"].get().strip()
    
    def on_ctrl_pressed(self, event):
        """Ctrl键按下事件 - 快速获取鼠标坐标"""
        x, y = pyautogui.position()
        
        # 获取当前焦点的组件
        focused_widget = self.master.focus_get()
        
        # 只为当前焦点的鼠标坐标输入框填入坐标
        if focused_widget:
            for button_name, mapping in self.button_mappings.items():
                if (mapping["action_type"] == "鼠标点击" and 
                    "mouse_entry" in mapping and 
                    mapping["mouse_entry"] == focused_widget):
                    mapping["mouse_entry"].delete(0, tk.END)
                    mapping["mouse_entry"].insert(0, f"{x},{y}")
                    self.update_mouse_config(button_name)
                    self.status_var.set(f"已为 {button_name} 设置坐标: ({x}, {y})")
                    self.master.after(3000, lambda: self.status_var.set("就绪"))
                    return
        
        # 如果没有焦点或焦点不是坐标输入框，则提示用户
        self.status_var.set(f"请先点击要设置坐标的输入框，当前坐标: ({x}, {y})")
        self.master.after(3000, lambda: self.status_var.set("就绪"))
    
    def save_config(self):
        """保存配置"""
        config = {}
        for button_name, mapping in self.button_mappings.items():
            config[button_name] = {
                "action_type": mapping["action_type"],
                "mouse_x": mapping["mouse_x"],
                "mouse_y": mapping["mouse_y"],
                "keyboard_key": mapping["keyboard_key"]
            }
        
        if self.config_manager.save_config(config):
            messagebox.showinfo("成功", "配置已保存")
            self.status_var.set("配置已保存")
        else:
            messagebox.showerror("错误", "保存配置失败")
    
    def save_config_as(self):
        """另存为配置"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="保存配置文件"
        )
        
        if filename:
            config = {}
            for button_name, mapping in self.button_mappings.items():
                config[button_name] = {
                    "action_type": mapping["action_type"],
                    "mouse_x": mapping["mouse_x"],
                    "mouse_y": mapping["mouse_y"],
                    "keyboard_key": mapping["keyboard_key"]
                }
            
            if self.config_manager.save_config(config, filename):
                messagebox.showinfo("成功", f"配置已保存到 {os.path.basename(filename)}")
                self.status_var.set(f"配置已保存到 {os.path.basename(filename)}")
            else:
                messagebox.showerror("错误", "保存配置失败")
    
    def load_config_dialog(self):
        """加载配置对话框"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="选择配置文件"
        )
        
        if filename:
            self.load_configuration(filename)
    
    def load_configuration(self, filename=None):
        """加载配置"""
        config = self.config_manager.load_config(filename)
        
        if config:
            for button_name, button_config in config.items():
                if button_name in self.button_mappings:
                    mapping = self.button_mappings[button_name]
                    
                    # 更新配置
                    mapping["action_type"] = button_config.get("action_type", "无动作")
                    mapping["mouse_x"] = button_config.get("mouse_x", "")
                    mapping["mouse_y"] = button_config.get("mouse_y", "")
                    mapping["keyboard_key"] = button_config.get("keyboard_key", "")
                    
                    # 更新界面
                    mapping["action_type_var"].set(mapping["action_type"])
                    
                    if mapping["action_type"] == "鼠标点击" and mapping["mouse_x"] and mapping["mouse_y"]:
                        mapping["mouse_entry"].delete(0, tk.END)
                        mapping["mouse_entry"].insert(0, f"{mapping['mouse_x']},{mapping['mouse_y']}")
                    elif mapping["action_type"] == "键盘按键" and mapping["keyboard_key"]:
                        mapping["keyboard_entry"].delete(0, tk.END)
                        mapping["keyboard_entry"].insert(0, mapping["keyboard_key"])
                    
                    # 更新显示
                    self.on_action_type_changed(button_name)
            
            filename_display = os.path.basename(filename) if filename else "默认配置"
            self.status_var.set(f"已加载配置: {filename_display}")
    
    def start_mapping(self):
        """启动映射"""
        if not self.controller.is_connected:
            # 尝试重新初始化手柄
            pygame.joystick.quit()
            pygame.joystick.init()
            if not self.controller.reconnect():
                messagebox.showerror("错误", "手柄未连接，请检查手柄连接")
                return

        self.running = True

        # 重新创建鼠标移动控制器（因为stop后线程已终止）
        self.state = {'alive': True, 'sleep': False}
        self.mouse_motion = MouseMotion(self.state)

        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_var.set("映射已启动")
    
    def stop_mapping(self):
        """停止映射"""
        self.running = False
        self.state['alive'] = False

        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_var.set("映射已停止")
    
    def start_main_loop(self):
        """启动主循环"""
        self.update_mouse_position()
        self.check_controller_input()
    
    def update_mouse_position(self):
        """更新鼠标位置显示"""
        try:
            x, y = pyautogui.position()
            self.mouse_coords_var.set(f"鼠标位置: X={x}, Y={y}")
        except:
            pass
        
        self.master.after(100, self.update_mouse_position)
    
    def check_controller_input(self):
        """检查手柄输入"""
        if self.running:
            button_states = self.controller.get_button_states()

            if not button_states and self.controller.is_connected:
                # 手柄可能断开连接
                self.controller.is_connected = False
                self.status_var.set("手柄连接丢失")
                print("手柄连接丢失")
            
            # 处理按键输入 - 添加防抖动逻辑
            for button_name, pressed in button_states.items():
                # 获取上一次的按键状态
                last_pressed = self.last_button_states.get(button_name, False)

                # 只在按键从未按下变为按下时触发动作（防抖动）
                if pressed and not last_pressed:
                    print(f"按键触发: {button_name}")
                    self.execute_action(button_name)

                # 更新按键状态
                self.last_button_states[button_name] = pressed

            # 处理摇杆映射鼠标
            if self.joystick_mouse_enabled.get():
                self.handle_joystick_mouse()
        else:
            pass
        
        self.master.after(50, self.check_controller_input)
    
    def execute_action(self, button_name):
        """执行按键动作"""
        if button_name not in self.button_mappings:
            return

        mapping = self.button_mappings[button_name]
        action_type = mapping["action_type"]

        try:
            if action_type == "鼠标点击":
                if mapping["mouse_x"] and mapping["mouse_y"]:
                    x, y = int(mapping["mouse_x"]), int(mapping["mouse_y"])
                    pyautogui.click(x, y)
                    self.status_var.set(f"执行鼠标点击: ({x}, {y})")

            elif action_type == "键盘按键":
                if mapping["keyboard_key"]:
                    pyautogui.press(mapping["keyboard_key"])
                    self.status_var.set(f"执行按键: {mapping['keyboard_key']}")

        except Exception as e:
            print(f"执行动作失败: {e}")
            self.status_var.set(f"动作执行失败: {button_name}")
    
    def handle_joystick_mouse(self):
        """处理摇杆映射鼠标移动 - 使用连续移动模式"""
        if not self.controller.is_connected:
            return
        
        joystick_axes = self.controller.get_joystick_axes()
        if not joystick_axes:
            # 如果获取摇杆状态失败，尝试重新连接
            if not self.controller.reconnect():
                return
            joystick_axes = self.controller.get_joystick_axes()
            if not joystick_axes:
                return
        
        # 如果禁用了摇杆鼠标，停止移动
        if not self.joystick_mouse_enabled.get():
            self.mouse_motion.set_velocity(0, 0)
            return
        
        # 根据选择的摇杆获取轴值
        if self.joystick_selection.get() == "左摇杆":
            x_axis, y_axis = joystick_axes.get("left", (0, 0))
        else:
            x_axis, y_axis = joystick_axes.get("right", (0, 0))
        
        # 检测并修复右摇杆Y轴漂移问题（仅在静止状态）
        drift_corrected = False
        if self.joystick_selection.get() == "右摇杆":
            # 检测Y轴漂移：Y轴精确为-1.0且X轴接近0，且持续时间超过阈值
            if abs(y_axis + 1.0) < 0.001 and abs(x_axis) < 0.01:  # 更严格的条件
                # 初始化漂移计数器
                if not hasattr(self, '_drift_counter'):
                    self._drift_counter = 0
                self._drift_counter += 1
                
                # 连续检测到漂移超过10次才修正，避免误判
                if self._drift_counter > 10:
                    y_axis = 0
                    drift_corrected = True
                    if not hasattr(self, '_drift_warning_shown'):
                        print("检测到右摇杆Y轴持续漂移，已自动修正")
                        self._drift_warning_shown = True
            else:
                # 重置漂移计数器
                if hasattr(self, '_drift_counter'):
                    self._drift_counter = 0
        
        # 调试输出摇杆状态（排除漂移修正的情况）
        if not drift_corrected and (abs(x_axis) > 0.05 or abs(y_axis) > 0.05):
            print(f"摇杆状态 - {self.joystick_selection.get()}: X={x_axis:.3f}, Y={y_axis:.3f}")
        
        # 获取扳机状态用于速度倍率控制
        button_states = self.controller.get_button_states()
        trigger_multiplier = 0
        if button_states and button_states.get('LT', False):  # 左扳机加速
            trigger_multiplier = 1.0
        
        # 设置鼠标移动速度和倍率
        self.mouse_motion.set_velocity(x_axis, y_axis)
        self.mouse_motion.set_multiplier(trigger_multiplier)
        
        # 调试输出（仅在有明显移动时）
        if abs(x_axis) > 0.1 or abs(y_axis) > 0.1:
            multiplier_text = f" (倍率: {trigger_multiplier:.1f}x)" if trigger_multiplier > 0 else ""
            print(f"鼠标速度设置: X={x_axis:.3f}, Y={y_axis:.3f}{multiplier_text}")

    def auto_start_mapping(self):
        """自动启动映射功能"""
        if self.controller.is_connected:
            print("自动启动映射功能")  # 调试输出
            self.start_mapping()
        else:
            print("手柄未连接，无法自动启动映射")
    
    def on_closing(self):
        """窗口关闭事件"""
        self.running = False
        self.state['alive'] = False
        self.mouse_motion.stop()
        self.master.destroy()

def main():
    """主函数"""
    root = tk.Tk()
    app = XboxControllerMapperGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()