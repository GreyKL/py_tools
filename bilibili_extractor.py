import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import os


# ---------------- 核心逻辑 ----------------
def process_video(event=None):  # 【修改点1】这里加一个 event=None，为了支持回车键
    # 【修改点2】在终端打印调试信息，用来判断点击是否真的生效了
    print("====== 正在触发提取指令！======")

    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("提示", "请输入视频地址")
        return

    # 1. 改变 UI 状态
    start_btn.config(state=tk.DISABLED, text="正在处理...")
    progress_bar.start(10)
    status_var.set("状态：1/4 正在启动后台线程...")
    result_text.delete(1.0, tk.END)

    # 2. 【关键修复】强制立刻刷新界面！防止 UI 被后续任务卡死导致看起来没反应
    window.update()

    # 3. 启动子线程
    threading.Thread(target=run_task, args=(url,), daemon=True).start()


def run_task(url):
    temp_audio = "temp_audio.mp3"
    try:
        # 步骤 1: 导入重度依赖库
        update_status("状态：2/4 正在加载 AI 运行环境 (若卡在此处请耐心等待几十秒)...")
        import yt_dlp
        import whisper

        # 步骤 2: 下载
        update_status("状态：3/4 正在解析网页并下载音频流...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'temp_audio.%(ext)s',
            'quiet': True, 'noplaylist': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # 步骤 3: 加载模型与识别
        update_status("状态：4/4 音频下载成功，AI 正在转写文案 (较慢，请勿关闭)...")
        model = whisper.load_model("small")
        result = model.transcribe(temp_audio, language="zh")

        # 步骤 4: 完成
        window.after(0, lambda: result_text.insert(tk.END, result["text"]))
        update_status("状态：✅ 提取成功！")

    except Exception as e:
        update_status(f"状态：❌ 处理出错")
        window.after(0, lambda: messagebox.showerror("发生错误", f"详细报错信息:\n{str(e)}"))
    finally:
        # 清理临时文件
        if os.path.exists(temp_audio):
            try:
                os.remove(temp_audio)
            except:
                pass
        # 恢复 UI 状态
        window.after(0, reset_ui)


def update_status(msg):
    """跨线程更新 UI 状态"""
    window.after(0, lambda: status_var.set(msg))


def reset_ui():
    """任务结束后的 UI 恢复"""
    progress_bar.stop()
    start_btn.config(state=tk.NORMAL, text="开始提取")


# ---------------- GUI 布局 ----------------
window = tk.Tk()
window.title("B站视频文案一键助手")
window.geometry("700x600")
window.configure(bg="#F1F2F3")

window.lift()
window.attributes('-topmost', True)
window.after_idle(window.attributes, '-topmost', False)

main_frame = tk.Frame(window, bg="#F1F2F3", padx=30, pady=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# 标题
tk.Label(main_frame, text="视频音频转文字工具", font=("微软雅黑", 18, "bold"), fg="#18191C", bg="#F1F2F3").pack(
    pady=(0, 20))

# ================= 替换这一段 =================
# 输入区
input_frame = tk.Frame(main_frame, bg="#F1F2F3")
input_frame.pack(fill=tk.X, pady=5)
tk.Label(input_frame, text="视频 URL:", font=("微软雅黑", 10), bg="#F1F2F3").pack(side=tk.LEFT)
url_entry = tk.Entry(input_frame, font=("微软雅黑", 11), bd=1, relief=tk.SOLID)
url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, ipady=4)
url_entry.focus_set()

# 【绝招 1：绑定回车键】在输入框里按回车，直接开始提取！
url_entry.bind('<Return>', process_video)

# 状态栏
status_var = tk.StringVar(value="状态：就绪，等待输入")
status_label = tk.Label(main_frame, textvariable=status_var, font=("微软雅黑", 10, "bold"), fg="#FF5722", bg="#F1F2F3")
status_label.pack(pady=(15, 5), anchor="w")

# 进度条
progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode='indeterminate', length=400)
progress_bar.pack(fill=tk.X, pady=5)

# 【绝招 2：改用 Label 伪装成按钮，强制绑定左键点击事件】
# Mac 上原生 Button 经常出毛病，Label 的点击事件是最稳的
start_btn = tk.Label(
    main_frame,
    text="开始提取 (或按回车)",
    bg="#D3D3D3",     # 浅灰色背景
    fg="black",       # 黑色文字
    font=("微软雅黑", 12, "bold"),
    cursor="hand2",
    padx=40,
    pady=10,
    relief=tk.RAISED, # 伪装成凸起的按钮
    bd=2
)
start_btn.pack(pady=15)
start_btn.bind('<Button-1>', process_video) # 强制绑定鼠标左键点击
# ============================================

# 结果展示
tk.Label(main_frame, text="识别文案：", font=("微软雅黑", 10, "bold"), bg="#F1F2F3", fg="#18191C").pack(anchor="w")
result_text = scrolledtext.ScrolledText(main_frame, font=("微软雅黑", 10), bg="white", bd=0, padx=10, pady=10)
result_text.pack(fill=tk.BOTH, expand=True, pady=10)

window.mainloop()