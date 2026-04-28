"""HTML 转 PDF 工具 - 基于 Playwright，支持 GUI (pywebview) 和 CLI"""

import argparse
import os
import subprocess
import sys
import threading
import traceback
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


def _get_playwright_cache():
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "ms-playwright"
    elif sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "ms-playwright"
    else:
        return Path.home() / ".cache" / "ms-playwright"


def ensure_playwright():
    if HAS_PLAYWRIGHT:
        cache = _get_playwright_cache()
        if not cache.exists() or not any(cache.iterdir()):
            print("正在安装 Chromium 浏览器，请稍候...")
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        return True
    print("正在安装 playwright，请稍候...")
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
    return True


def html_to_pdf(input_path: str, output_path: str, size: str, margin: str, background: bool):
    input_file = Path(input_path).resolve()
    if not input_file.exists():
        raise FileNotFoundError(f"文件不存在: {input_file}")
    url = input_file.as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        page.pdf(
            path=output_path,
            format=size,
            margin={"top": margin, "right": margin, "bottom": margin, "left": margin},
            print_background=background,
        )
        browser.close()
    return output_path


# ─── CLI 模式 ───

def cli_main():
    parser = argparse.ArgumentParser(description="HTML 转 PDF 工具")
    parser.add_argument("input", help="输入 HTML 文件路径")
    parser.add_argument("-o", "--output", help="输出 PDF 路径（默认与输入同名）")
    parser.add_argument("--size", default="A4", help="纸张大小（默认 A4）")
    parser.add_argument("--margin", default="10mm", help="页边距（默认 10mm）")
    parser.add_argument("--no-background", action="store_true", help="不打印背景色/图片")
    args = parser.parse_args()
    output = args.output or str(Path(args.input).with_suffix(".pdf"))
    ensure_playwright()
    html_to_pdf(args.input, output, args.size, args.margin, not args.no_background)
    print(f"已生成: {output}")


# ─── GUI 模式 (pywebview) ───

HTML_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; padding: 20px; background: #f5f5f7; color: #1d1d1f; }
h1 { font-size: 18px; font-weight: 600; margin-bottom: 16px; }
.group { background: #fff; border-radius: 10px; padding: 14px 16px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.group label { display: block; font-size: 13px; color: #86868b; margin-bottom: 6px; }
.row { display: flex; gap: 8px; align-items: center; }
.row input[type="text"] { flex: 1; padding: 7px 10px; border: 1px solid #d2d2d7; border-radius: 6px; font-size: 14px; outline: none; }
.row input[type="text"]:focus { border-color: #007aff; }
button { padding: 7px 16px; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; white-space: nowrap; }
.btn-browse { background: #e8e8ed; color: #1d1d1f; }
.btn-browse:hover { background: #d8d8dc; }
.btn-convert { background: #007aff; color: #fff; font-weight: 500; padding: 9px 24px; font-size: 15px; }
.btn-convert:hover { background: #0066d6; }
.btn-convert:disabled { background: #b0b0b6; cursor: not-allowed; }
.options { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
.options select, .options input[type="text"] { padding: 6px 8px; border: 1px solid #d2d2d7; border-radius: 6px; font-size: 13px; }
.options select { width: 90px; }
.options input[type="text"] { width: 70px; }
.options label { display: flex; align-items: center; gap: 4px; font-size: 13px; color: #1d1d1f; cursor: pointer; }
.action-row { display: flex; align-items: center; gap: 12px; margin-top: 4px; }
#status { font-size: 13px; color: #86868b; }
#status.error { color: #ff3b30; }
#status.success { color: #34c759; }
</style>
</head>
<body>
<h1>HTML 转 PDF</h1>

<div class="group">
  <label>输入 HTML 文件</label>
  <div class="row">
    <input type="text" id="input_path" placeholder="点击浏览选择文件...">
    <button class="btn-browse" onclick="browseInput()">浏览</button>
  </div>
</div>

<div class="group">
  <label>输出 PDF 路径</label>
  <div class="row">
    <input type="text" id="output_path" placeholder="点击浏览选择保存位置...">
    <button class="btn-browse" onclick="browseOutput()">浏览</button>
  </div>
</div>

<div class="group">
  <div class="options">
    <label>纸张大小
      <select id="page_size">
        <option value="A4" selected>A4</option>
        <option value="A3">A3</option>
        <option value="Letter">Letter</option>
        <option value="Legal">Legal</option>
        <option value="Tabloid">Tabloid</option>
      </select>
    </label>
    <label>页边距
      <input type="text" id="margin" value="10mm">
    </label>
    <label><input type="checkbox" id="bg" checked> 打印背景</label>
  </div>
</div>

<div class="action-row">
  <button class="btn-convert" id="btn_convert" onclick="doConvert()">转换为 PDF</button>
  <span id="status">就绪</span>
</div>

<script>
async function browseInput() {
  try {
    const result = await pywebview.api.browse_input();
    if (result) {
      document.getElementById('input_path').value = result.input;
      if (result.output) document.getElementById('output_path').value = result.output;
    }
  } catch(e) { console.error(e); }
}

async function browseOutput() {
  try {
    const result = await pywebview.api.browse_output();
    if (result) document.getElementById('output_path').value = result;
  } catch(e) { console.error(e); }
}

async function doConvert() {
  const btn = document.getElementById('btn_convert');
  const status = document.getElementById('status');
  btn.disabled = true;
  status.className = '';
  status.textContent = '正在转换...';

  const params = {
    input: document.getElementById('input_path').value.trim(),
    output: document.getElementById('output_path').value.trim(),
    size: document.getElementById('page_size').value,
    margin: document.getElementById('margin').value,
    background: document.getElementById('bg').checked
  };

  try {
    const result = await pywebview.api.convert(params);
    if (result.ok) {
      status.className = 'success';
      status.textContent = '转换完成! ' + result.path;
    } else {
      status.className = 'error';
      status.textContent = '失败: ' + result.error;
    }
  } catch(e) {
    status.className = 'error';
    status.textContent = '异常: ' + e;
  } finally {
    btn.disabled = false;
  }
}
</script>
</body>
</html>
"""


class Api:
    """pywebview 暴露给 JS 的 Python 接口"""

    def __init__(self, window):
        self.window = window

    def browse_input(self):
        import webview
        result = self.window.create_file_dialog(
            webview.FileDialog.OPEN,
            directory="",
            file_types=("HTML 文件 (*.html;*.htm)", "所有文件 (*.*)"),
        )
        if result and len(result) > 0:
            path = result[0]
            output = str(Path(path).with_suffix(".pdf"))
            return {"input": path, "output": output}
        return None

    def browse_output(self):
        import webview
        result = self.window.create_file_dialog(
            webview.FileDialog.SAVE,
            directory="",
            save_filename="output.pdf",
            file_types=("PDF 文件 (*.pdf)", "所有文件 (*.*)"),
        )
        if result and len(result) > 0:
            return result[0]
        return None

    def convert(self, params):
        input_path = params.get("input", "").strip()
        output_path = params.get("output", "").strip()
        size = params.get("size", "A4")
        margin = params.get("margin", "10mm")
        background = params.get("background", True)

        if not input_path:
            return {"ok": False, "error": "请选择 HTML 文件"}
        if not output_path:
            return {"ok": False, "error": "请指定输出 PDF 路径"}
        if not Path(input_path).exists():
            return {"ok": False, "error": f"文件不存在: {input_path}"}

        try:
            ensure_playwright()
            html_to_pdf(input_path, output_path, size, margin, background)
            return {"ok": True, "path": output_path}
        except Exception as e:
            return {"ok": False, "error": str(e)}


def gui_main():
    import webview

    class _Api(Api):
        """延迟获取 window 引用"""
        def __init__(self):
            pass

        @property
        def window(self):
            return webview.windows[0]

    api = _Api()
    webview.create_window("HTML 转 PDF", html=HTML_PAGE, width=480, height=420,
                          resizable=False, js_api=api)
    webview.start()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_main()
    else:
        gui_main()
