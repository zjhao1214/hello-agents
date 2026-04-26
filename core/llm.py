# HelloAgentsLLM统一接口
import os
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 文件中的环境变量
load_dotenv()

class HelloAgentsLLM:
    """
    为本书 "Hello Agents" 定制的LLM客户端。
    它用于调用任何兼容OpenAI接口的服务，并默认使用流式响应。
    """
    def __init__(self, model:str = None, api_key:str = None, base_url:str = None, timeout:int = None):
        """
        初始化客户端。优先使用传入参数，如果未提供，则从环境变量加载。
        支持自动检测provider或使用统一的LLM_*环境变量配置。

        Args:
            model: 模型名称，如果未提供则从环境变量LLM_MODEL_ID读取
            api_key: API密钥，如果未提供则从环境变量读取
            base_url: 服务地址，如果未提供则从环境变量LLM_BASE_URL读取
            provider: LLM提供商，如果未提供则自动检测
            temperature: 温度参数
            max_tokens: 最大token数
            timeout: 超时时间，从环境变量LLM_TIMEOUT读取，默认60秒
        """
        self.model = model or os.getenv("LLM_MODEL_ID")
        api_key = api_key or os.environ.get("LLM_API_KEY")
        base_url = base_url or os.environ.get("LLM_BASE_URL")
        timeout  = base_url or int(os.environ.get("LLM_TIMEOUT", 60))

        if not all([self.model, api_key, base_url]):
            return ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    def think(self, messages:List[Dict[str, str]], temperature:float = 0 ) -> str:
        """
        调用大语言模型进行思考，并返回其响应。
        """
        print(f"🧠 正在调用 {self.model} 模型...")
        try:
            response = self.client.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )
            # 处理流式响应
            print("✅ 大语言模型响应成功:")
            collected_content = []
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)
        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return None

def main():
    llm = HelloAgentsLLM()

if __name__ == "__main__":
    main()