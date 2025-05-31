#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Xbox手柄映射器 v1.0
一个功能强大的Xbox手柄按键映射工具
支持将手柄按键映射为鼠标点击或键盘按键
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import pyautogui
import json
import os
import time
import threading
from typing import Dict, Any

# 优化PyAutoGUI性能
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.PAUSE = 0

class XboxControllerMapper:
    """Xbox手柄映射器核心类"""
    
    def __init__(self):
        # 初始化pygame
        pygame.init()
        pygame.joystick.init()
        
        # 手柄相关
        self.joystick = None
        self.connected = False
        self.running = False
        
        # 按键映射配置
        self.mappings = {}
        self.button_states = {}
        self.previous_states = {}
        
        # 支持的按键列表
        self.buttons = ['A', 'B', 'X', 'Y', 'LB', 'RB', 'LT', 'RT', 
                       'Back', 'Start', 'LS', 'RS', 'Up', 'Down', 'Left', 'Right']
        
        # 加载配置
        self.load_config()
        
    def check_controller_connection(self):
        """检查手柄连接状态"""
        try:
            pygame.joystick.quit()
            pygame.joystick.init()
            
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.connected = True
                return True
            else:
                self.connected = False
                return False
        except Exception as e:
            print(f"手柄连接检查错误: {e}")
            self.connected = False
            return False
    
    def get_button_states(self):
        """获取按键状态"""
        if not self.connected or not self.joystick:
            return {}
        
        try:
            pygame.event.pump()
            states = {}
            
            # 获取普通按键状态
            button_map = {
                0: 'A', 1: 'B', 2: 'X', 3: 'Y',
                4: 'LB', 5: 'RB', 6: 'Back', 7: 'Start',
                8: 'LS', 9: 'RS'
            }
            
            for i, button_name in button_map.items():
                if i < self.joystick.get_numbuttons():
                    states[button_name] = self.joystick.get_button(i)
            
            # 获取方向键状态
            if self.joystick.get_numhats() > 0:
                hat = self.joystick.get_hat(0)
                states['Up'] = hat[1] == 1
                states['Down'] = hat[1] == -1
                states['Left'] = hat[0] == -1
                states['Right'] = hat[0] == 1
            
            # 获取扳机键状态（轴检测）
            if self.joystick.get_numaxes() >= 6:
                # LT通常在轴4，RT在轴5
                lt_axis = self.joystick.get_axis(4) if self.joystick.get_numaxes() > 4 else -1
                rt_axis = self.joystick.get_axis(5) if self.joystick.get_numaxes() > 5 else -1
                
                # 标准化轴值（-1到1转换为0到1）
                lt_normalized = (lt_axis + 1) / 2
                rt_normalized = (rt_axis + 1) / 2
                
                states['LT'] = lt_normalized > 0.1
                states['RT'] = rt_normalized > 0.1
            
            return states
            
        except Exception as e:
            print(f"获取按键状态错误: {e}")
            return {}
    
    def execute_action(self, button_name):
        """执行按键映射动作"""
        if button_name not in self.mappings:
            return
        
        mapping = self.mappings[button_name]
        action_type = mapping.get('action_type', '无动作')
        
        try:
            if action_type == '鼠标左键':
                pyautogui.click(button='left')
            elif action_type == '鼠标右键':
                pyautogui.click(button='right')
            elif action_type == '键盘按键':
                key = mapping.get('keyboard_key', '')
                if key:
                    pyautogui.press(key)
            elif action_type == '鼠标坐标':
                x = int(mapping.get('mouse_x', 0))
                y = int(mapping.get('mouse_y', 0))
                if x > 0 and y > 0:
                    pyautogui.click(x, y)
            
            print(f"执行动作: {button_name} -> {action_type}")
            
        except Exception as e:
            print(f"执行动作错误: {e}")
    
    def check_controller_input(self):
        """检查手柄输入（主循环）"""
        while self.running:
            if not self.connected:
                time.sleep(0.1)
                continue
            
            current_states = self.get_button_states()
            
            # 检查按键变化（防抖动）
            for button_name in self.buttons:
                current = current_states.get(button_name, False)
                previous = self.previous_states.get(button_name, False)
                
                # 只在按键从未按下变为按下时触发
                if current and not previous:
                    self.execute_action(button_name)
            
            self.previous_states = current_states.copy()
            time.sleep(0.05)  # 50ms检查间隔
    
    def start_mapping(self):
        """开始映射"""
        if not self.connected:
            print("手柄未连接")
            return False
        
        self.running = True
        self.mapping_thread = threading.Thread(target=self.check_controller_input, daemon=True)
        self.mapping_thread.start()
        print("映射已启动")
        return True
    
    def stop_mapping(self):
        """停止映射"""
        self.running = False
        print("映射已停止")
    
    def load_config(self):
        """加载配置文件"""
        config_files = ['controller_config.json', 'xbox_config.json']
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        self.mappings = json.load(f)
                    print(f"已加载配置: {config_file}")
                    return
                except Exception as e:
                    print(f"加载配置文件错误: {e}")
        
        # 创建默认配置
        self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置"""
        self.mappings = {}
        for button in self.buttons:
            self.mappings[button] = {
                'action_type': '无动作',
                'mouse_x': '',
                'mouse_y': '',
                'keyboard_key': ''
            }
        
        self.save_config()
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open('controller_config.json', 'w', encoding='utf-8') as f:
                json.dump(self.mappings, f, ensure_ascii=False, indent=2)
            print("配置已保存")
        except Exception as e:
            print(f"保存配置错误: {e}")

class XboxControllerMapperGUI:
    """图形用户界面类"""
    
    def __init__(self, master):
        self.master = master
        self.master.title("Xbox手柄映射器 v1.0")
        self.master.geometry("800x600")
        
        # 初始化控制器
        self.controller = XboxControllerMapper()
        
        # 创建界面
        self.create_widgets()
        
        # 启动状态检查
        self.check_status()
        
        # 绑定关闭事件
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态显示
        status_frame = ttk.LabelFrame(main_frame, text="状态信息", padding="10")
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="手柄状态：检测中...")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 控制按钮
        control_frame = ttk.LabelFrame(main_frame, text="控制", padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_button = ttk.Button(control_frame, text="开始映射", command=self.start_mapping)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="停止映射", command=self.stop_mapping)
        self.stop_button.grid(row=0, column=1)
        
        # 按键配置区域
        config_frame = ttk.LabelFrame(main_frame, text="按键配置", padding="10")
        config_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建按键配置界面
        self.create_button_config(config_frame)
    
    def create_button_config(self, parent):
        """创建按键配置界面"""
        # 简化的按键配置界面
        ttk.Label(parent, text="按键配置功能正在开发中...").grid(row=0, column=0)
        ttk.Label(parent, text="请手动编辑 controller_config.json 文件进行配置").grid(row=1, column=0)
    
    def check_status(self):
        """检查手柄状态"""
        if self.controller.check_controller_connection():
            joystick_name = self.controller.joystick.get_name() if self.controller.joystick else "未知手柄"
            self.status_label.config(text=f"手柄状态：已连接 - {joystick_name}")
        else:
            self.status_label.config(text="手柄状态：未连接")
        
        # 每秒检查一次
        self.master.after(1000, self.check_status)
    
    def start_mapping(self):
        """开始映射"""
        if self.controller.start_mapping():
            messagebox.showinfo("成功", "映射已启动")
        else:
            messagebox.showerror("错误", "手柄未连接，无法启动映射")
    
    def stop_mapping(self):
        """停止映射"""
        self.controller.stop_mapping()
        messagebox.showinfo("信息", "映射已停止")
    
    def on_closing(self):
        """窗口关闭事件"""
        self.controller.stop_mapping()
        self.master.destroy()

def main():
    """主函数"""
    root = tk.Tk()
    app = XboxControllerMapperGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
