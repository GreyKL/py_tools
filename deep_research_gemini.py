import time
import os
import sys
from dotenv import load_dotenv
from google import genai

# 强制将控制台输出编码设置为 UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# 从 .env 文件加载环境变量
load_dotenv()

# 从环境变量读取 API Key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API Key 没获取到！请检查配置。")

# 显式传入 api_key 初始化客户端
client = genai.Client(api_key=api_key)

def analyze_document_with_deep_research(file_path: str, prompt: str):
    # 步骤 1: 上传本地文件到 Google 云端
    print(f"正在上传文件: {file_path} ...")
    try:
        uploaded_file = client.files.upload(file=file_path)
        print(f"文件上传成功。文件 URI: {uploaded_file.uri}")
    except Exception as e:
        print(f"❌ 文件上传失败，请检查文件是否被占用或路径错误: {e}")
        return

    print("正在启动 Deep Research Agent 进行深度分析...")

    # 步骤 2: 使用 interactions API 触发后台长时任务（不要用 generate_content）
    try:
        interaction = client.interactions.create(
            # 使用标准的底层 Agent 代号
            agent="deep-research-pro-preview-12-2025",
            input=[uploaded_file, prompt],
            background=True  # 【关键】开启后台异步运行
        )
        print(f"任务已成功在云端启动！Interaction ID: {interaction.id}")
        print("Agent 正在结合文件内容与全网数据进行深度研究，这通常需要几分钟到数十分钟，请耐心等待...")
    except Exception as e:
        print(f"\n❌ 启动 Agent 失败: {e}")
        return

    # 步骤 3: 轮询检查云端任务状态
    while True:
        try:
            status_check = client.interactions.get(id=interaction.id)
            state = status_check.status
            print(f"当前状态: {state} ...")

            if state == "completed":
                print("\n" + "=" * 50)
                print("🎉 分析报告生成完毕：\n")
                # 提取最后一次的输出内容
                print(status_check.outputs[-1].text)
                break
            elif state in ["failed", "cancelled"]:
                print(f"\n❌ 任务未成功，最终状态: {state}")
                if hasattr(status_check, 'error'):
                    print(f"错误信息: {status_check.error}")
                break
        except Exception as e:
            print(f"⚠️ 查询进度时遇到网络波动: {e}，将继续重试...")

        # 考虑到研究耗时较长，每 15 秒查询一次
        time.sleep(15)


if __name__ == "__main__":
    # 你的 Excel 文件路径
    local_file = "/Users/kuangli/Desktop/analy_jj/retail_data.xlsx"

    # 你的研究指令
    research_prompt = """
    请仔细阅读我提供的文件内容。
    分析将军大道支行该季度业务情况
    """

    if os.path.exists(local_file):
        analyze_document_with_deep_research(local_file, research_prompt)
    else:
        print(f"找不到文件，请检查路径是否正确: {local_file}")