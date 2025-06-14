# 手柄映射器 v1.0

一个功能强大的Xbox手柄按键映射工具，支持将手柄按键映射为鼠标点击或键盘按键。

## 功能特性

- 🎮 **Xbox手柄支持**: 完美支持Xbox有线/无线手柄
- 🖱️ **鼠标映射**: 将手柄按键映射为鼠标左键/右键点击
- ⌨️ **键盘映射**: 将手柄按键映射为任意键盘按键
- 🎯 **坐标映射**: 支持鼠标点击指定屏幕坐标
- 🔄 **实时检测**: 实时显示手柄连接状态和按键状态
- 💾 **配置保存**: 自动保存映射配置，下次启动自动加载
- 🎨 **友好界面**: 简洁直观的图形用户界面

## 软件界面截图
![软件界面截图](docs/images/1748722979666(1).jpg)
## 支持的按键

- **方向键**: 上、下、左、右
- **功能键**: A、B、X、Y
- **肩键**: LB、RB
- **扳机键**: LT、RT
- **摇杆键**: LS、RS
- **系统键**: Back、Start

## 系统要求

- Windows 7/8/10/11
- Python 3.7+ (源码运行)
- Xbox手柄 (有线或无线)

## 快速开始

### 方式一：直接运行EXE文件
1. 下载最新版本的 `手柄映射器.exe`
2. 连接Xbox手柄到电脑
3. 双击运行程序
4. 等待手柄连接状态显示为"已连接"
5. 开始配置按键映射

### 方式二：源码运行
1. 克隆或下载本项目
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行主程序：
   ```bash
   python controller_mapper.py
   ```

## 使用说明

### 1. 连接手柄
- 确保Xbox手柄已正确连接到电脑
- 程序启动后会自动检测手柄
- 状态栏显示"手柄状态：已连接"表示连接成功

### 2. 配置按键映射
- 点击任意按键对应的"设置"按钮
- 选择映射类型：
  - **鼠标左键**: 映射为鼠标左键点击
  - **鼠标右键**: 映射为鼠标右键点击
  - **键盘按键**: 映射为指定的键盘按键
  - **鼠标坐标**: 映射为点击指定屏幕坐标
  - **无动作**: 禁用该按键

### 3. 开始映射
- 配置完成后，点击"开始映射"按钮
- 按下手柄按键即可触发对应的映射动作
- 点击"停止映射"可以停止映射功能

### 4. 保存配置
- 程序会自动保存当前的映射配置
- 下次启动时会自动加载上次的配置

## 下载

### EXE文件下载
- [手柄映射器.exe](https://github.com/EatWorld/controller-mapper/releases/latest) - Windows 7/10/11 兼容版本

### 源码下载
```bash
git clone https://github.com/EatWorld/controller-mapper.git
cd controller-mapper
pip install -r requirements.txt
python controller_mapper.py
```

## 配置文件

程序使用JSON格式保存配置：
- `controller_mappings.json`: 用户自定义映射配置
- `controller_config.json`: 程序设置配置
- `xbox_config.json`: Xbox手柄专用配置

## 故障排除

### 手柄无法连接
1. 确认手柄已正确连接到电脑
2. 检查Windows设备管理器中是否识别到手柄
3. 尝试重新插拔手柄或重启程序

### 按键映射无响应
1. 确认已点击"开始映射"按钮
2. 检查按键是否已正确配置
3. 确认目标应用程序处于活动状态

### RT/LT扳机键检测问题
- RT/LT扳机键使用模拟轴检测
- 轻微按压即可触发（阈值：10%）
- 如仍有问题，请检查手柄驱动程序

## 技术说明

- **开发语言**: Python 3.x
- **GUI框架**: Tkinter
- **手柄库**: Pygame
- **自动化库**: PyAutoGUI, Mouse
- **打包工具**: PyInstaller

## 更新日志

### v1.0 (2024-12-19)
- 🎉 首个正式版本发布
- ✅ 完整的Xbox手柄支持
- ✅ 鼠标和键盘映射功能
- ✅ 实时状态显示
- ✅ 配置保存和加载
- ✅ RT/LT扳机键优化检测
- ✅ 友好的用户界面
- ✅ Windows 7/10/11 兼容性

## 许可证

MIT License - 详见 LICENSE 文件

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 联系方式

如有问题或建议，请通过GitHub Issues联系。
