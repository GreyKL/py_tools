import os
import sys
from dotenv import load_dotenv
from google import genai

# 强制终端输出 UTF-8，防止中文乱码
sys.stdout.reconfigure(encoding='utf-8')

# 从 .env 文件加载环境变量
load_dotenv()

# 从环境变量读取 API Key
API_KEY = os.getenv("GEMINI_API_KEY")

# 初始化客户端
client = genai.Client(api_key=API_KEY)


def start_chat():
    print("🤖 欢迎使用 Gemini 终端助手！(输入 '退出' 或 'quit' 结束对话)\n")
    print("-" * 50)

    try:
        # client.chats.create 会创建一个包含上下文记忆的对话实例
        # 对于纯文本对话，强烈推荐使用 gemini-2.5-flash，速度极快且成本低
        # 如果需要极强的逻辑推理，可以改为 "gemini-2.5-pro"
        chat = client.chats.create(model="gemini-3.0-pro")

        while True:
            # 等待用户输入
            user_msg = input("\n你: ")

            # 处理退出指令
            if user_msg.strip().lower() in ['退出', 'quit', 'exit']:
                print("👋 结束对话，下次见！")
                break

            # 防止发送空消息报错
            if not user_msg.strip():
                continue

            # 发送消息给模型
            response = chat.send_message(user_msg)

            # 打印模型回复
            print(f"\nGemini: {response.text}")

    except KeyboardInterrupt:
        print("\n\n👋 强制结束对话，下次见！")
    except Exception as e:
        print(f"\n❌ 对话发生错误: {e}")


if __name__ == "__main__":
    start_chat()