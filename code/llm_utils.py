"""
LLM工具模块 - 提供统一的LLM调用接口
支持多种API源：OpenAI、Azure OpenAI、HKUST GenAI
"""

import os
import json
import streamlit as st
from typing import Optional, List, Dict, Any

# 尝试导入OpenAI
try:
    from openai import OpenAI
except ImportError:
    print("Warning: openai package not installed")

class LLMClient:
    MODELSCOPE_BASE_URL = "https://api-inference.modelscope.cn/v1"
    MODELSCOPE_DEFAULT_MODEL = "MiniMax/MiniMax-M2.5"
    """LLM客户端封装类"""

    def __init__(self, api_source: str = "openai", api_key: Optional[str] = None):
        """
        初始化LLM客户端

        Args:
            api_source: API来源，可选 "openai", "azure", "hkust"
            api_key: API密钥，如果为None则从环境变量读取
        """
        self.api_source = api_source

        if api_key:
            self.api_key = api_key
        elif api_source == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY", "")
        elif api_source == "modelscope":
            self.api_key = (
                os.getenv("MODELSCOPE_API_KEY")
                or "ms-aea9b1d5-44e4-4192-8c0d-db217485788d"
            )
        elif api_source in ["azure", "hkust"]:
            self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        else:
            self.api_key = ""

        # 初始化客户端
        if api_source == "openai" and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        elif api_source == "modelscope" and self.api_key:
            self.client = OpenAI(
                base_url=self.MODELSCOPE_BASE_URL,
                api_key=self.api_key
            )
        else:
            self.client = None

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> Any:
        """
        发送聊天请求到LLM

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            history: 对话历史列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            LLM的响应文本
        """
        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]

        # 添加历史对话
        if history:
            for msg in history:
                messages.append(msg)

        # 添加当前用户输入
        messages.append({"role": "user", "content": user_prompt})

        try:
            if self.client:
                if self.api_source == "modelscope" and model == "gpt-4o-mini":
                    model = self.MODELSCOPE_DEFAULT_MODEL

                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream
                )
                if stream:
                    def generate():
                        for chunk in response:
                            if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                                delta = chunk.choices[0].delta
                                if hasattr(delta, 'content') and delta.content is not None:
                                    yield delta.content
                    return generate()
                return response.choices[0].message.content
            else:
                if stream:
                    def error_gen():
                        yield "Error: No valid LLM client initialized. Please check your API key and source."
                    return error_gen()
                return "Error: No valid LLM client initialized. Please check your API key and source."
        except Exception as e:
            if stream:
                def error_gen():
                    yield f"Error: {str(e)}"
                return error_gen()
            return f"Error: {str(e)}"

def get_llm_client(api_source: str = "openai") -> LLMClient:
    """
    获取LLM客户端实例的工厂函数

    Args:
        api_source: API来源

    Returns:
        LLMClient实例
    """
    return LLMClient(api_source=api_source)


# 快捷函数
def quick_chat(
    user_prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    api_source: str = "openai"
) -> str:
    """
    快速聊天函数

    Args:
        user_prompt: 用户输入
        system_prompt: 系统提示
        api_source: API来源

    Returns:
        LLM响应
    """
    client = get_llm_client(api_source)
    return client.chat(system_prompt=system_prompt, user_prompt=user_prompt)
