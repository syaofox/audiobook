# 音频阅读器

一个简单的网页音频播放器，支持同步显示文本内容，适合用于有声读物、音频课程等场景。

## 主要功能

- 🔒 密码保护访问
- 📁 支持多级目录音频文件管理
- 🎵 音频播放（支持 mp3、wav 格式）
- 📝 同步显示对应文本内容
- 💾 自动保存播放进度和阅读进度
- 📱 响应式设计，支持手机访问

## 技术栈

- Python Flask
- Bootstrap 5
- HTML5 Audio
- localStorage

## 安装步骤

1. 克隆项目：

```bash
git clone https://github.com/syaofox/audio-reader.git
cd audio-reader
```

2. 安装 Python 依赖：

```bash
pip install -r requirements.txt
```

3. 目录结构：

```
audio-reader/
├── static/
│   ├── css/
│   ├── js/
│   └── audio/     # 存放音频文件
├── templates/     # HTML模板
├── texts/         # 文本文件
├── app.py         # 主程序
└── config.py      # 配置文件
```

4. 配置文件：
   - 复制 `config.example.py` 为 `config.py`
   - 修改访问密码和其他配置项
   - 可以通过环境变量 `AUDIO_FOLDER` 自定义音频文件目录，例如：
     ```bash
     # Linux/Mac
     export AUDIO_FOLDER="/path/to/your/audio/files"
     
     # Windows (CMD)
     set AUDIO_FOLDER=D:\your\audio\files
     
     # Windows (PowerShell)
     $env:AUDIO_FOLDER="D:\your\audio\files"
     ```

5. 运行服务：

```bash
python app.py
```

## 使用说明

1. 音频文件
   - 将音频文件(.mp3/.wav)放入 `static/audio` 目录
   - 支持多级子目录组织音频文件
   - 建议使用统一的命名规范，如：`01-chapter-name.mp3`

2. 文本文件
   - 在 `texts` 目录下创建与音频文件同名的.txt文件

3. 访问系统
   - 打开浏览器访问 `http://localhost:5000`
   - 输入配置的访问密码
   - 首次访问会要求设置访问密码

## 注意事项

- 建议使用现代浏览器访问（Chrome、Firefox、Safari等）
- 音频文件名请使用英文或数字，避免特殊字符
- 文本文件请使用UTF-8编码保存
- 系统会自动保存播放进度，重新打开时会从上次位置继续播放
- 如需清除播放记录，可以在浏览器中清除本站点的localStorage数据


## 开源协议

本项目采用 [MIT License](LICENSE) 开源许可证。
