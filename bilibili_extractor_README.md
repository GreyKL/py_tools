# bilibili_extractor.py 使用手册

## 功能说明

从 B 站视频提取音频并自动转写为文字。

## 安装依赖

```bash
pip install yt-dlp openai-whisper
```

**注意**：还需安装 [FFmpeg](https://ffmpeg.org/download.html)，用于音频处理。

## 启动方式

```bash
python bilibili_extractor.py
```

## 界面操作

1. **输入地址**：在输入框粘贴 B 站视频链接
2. **开始提取**：点击「开始提取」按钮，或直接按回车键
3. **等待处理**：状态栏会显示当前进度（下载音频 → AI 转写）
4. **查看结果**：转写完成的文字会显示在下方文本框

## 常见问题

- **卡在"加载 AI 运行环境"**：首次加载 Whisper 模型较慢，请耐心等待
- **下载失败**：确保 FFmpeg 已正确安装并添加到系统环境变量