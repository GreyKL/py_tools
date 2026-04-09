# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 Python 工具集合，包含多个独立的实用脚本。每个脚本都是独立运行的，没有统一的包结构或依赖管理。

## 脚本说明

| 文件 | 用途 | 运行方式 |
|------|------|----------|
| `two_sum.py` | LeetCode Two Sum 算法实现 | `python two_sum.py` |
| `remove_water.py` | GUI 图片去水印工具 | `python remove_water.py` |
| `gemini_chat.py` | 终端 Gemini 聊天客户端 | `python gemini_chat.py` |
| `deep_research_gemini.py` | Gemini Deep Research 文档分析 | `python deep_research_gemini.py` |

## 依赖

- `opencv-python` - 图片处理
- `numpy` - 数值计算
- `pillow` - 图像处理
- `google-genai` - Google Gemini API 客户端

安装依赖：`pip install opencv-python numpy pillow google-genai`

## 架构特点

- **无共享模块**：每个脚本独立运行，不依赖项目内其他文件
- **无测试框架**：算法脚本内嵌测试用例
- **硬编码配置**：API Key 等敏感信息直接写在代码中（使用时应移至环境变量）

## 注意事项

- Gemini 相关脚本中的 API Key 需要替换为有效密钥
- `remove_water.py` 使用 OpenCV 的 Telea 算法进行图像修复
- 所有脚本直接运行即可，无需构建步骤