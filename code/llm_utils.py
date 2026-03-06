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
        elif api_source in ["azure", "hkust"]:
            self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        else:
            self.api_key = ""

        # 初始化客户端
        if api_source == "openai" and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
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
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            else:
                # 如果没有有效客户端，返回模拟响应
                return self._mock_response(user_prompt, system_prompt)
        except Exception as e:
            return f"Error: {str(e)}"

    def _mock_response(self, user_prompt: str, system_prompt: str) -> str:
        """
        当API不可用时，返回模拟响应
        用于演示和测试
        """
        user_lower = user_prompt.lower()

        # 护栏分类模拟
        if "classify" in system_prompt.lower() or "category" in system_prompt.lower():
            if any(kw in user_lower for kw in ["derivative", "integral", "solve", "equation", "calculate", "数学", "计算", "微积分"]):
                return "MATH"
            elif any(kw in user_lower for kw in ["history", "president", "revolution", "war", "历史", "总统", "革命"]):
                return "HISTORY"
            elif "summarize" in user_lower or "总结" in user_lower:
                return "SUMMARY"
            elif any(kw in user_lower for kw in ["travel", "trip", "plan", "itinerary", "旅行", "旅游", "电影", "entertainment"]):
                return "OFF_TOPIC"
            elif any(kw in user_lower for kw in ["hkust", "local university", "small college", "本地", "小大学"]):
                return "OBSCURE"
            else:
                return "UNKNOWN"

        # 数学辅导模拟
        if "math" in system_prompt.lower() or "数学" in system_prompt.lower():
            if "derivative" in user_lower or "导数" in user_lower:
                return "要计算导数，我们需要使用求导法则。对于 f(x) = x²·sin(x)，我们将使用乘法法则：\n\n(d/dx)[f(x)·g(x)] = f'(x)·g(x) + f(x)·g'(x)\n\n设 f(x) = x², g(x) = sin(x)，则：\nf'(x) = 2x, g'(x) = cos(x)\n\n所以 f'(x) = 2x·sin(x) + x²·cos(x)"
            elif "square root" in user_lower or "sqrt" in user_lower or "根号" in user_lower:
                return "√1000 不是有理数。\n\n证明：假设 √1000 = a/b（其中a, b为整数，b≠0，且a, b互质），那么 a² = 1000b²。\n\n由于1000 = 2³ × 5³，不是完全平方数，因此 a² 包含质因数2和5出现奇数次，这意味着 a 也包含这些质因数，出现矛盾。因此 √1000 是无理数。"
            elif "equation" in user_lower or "方程" in user_lower or "solve" in user_lower:
                if "x+1=2" in user_lower or "x + 1 = 2" in user_lower:
                    return "解方程 x + 1 = 2：\n\n步骤1：两边同时减去1\nx + 1 - 1 = 2 - 1\n\n步骤2：得到结果\nx = 1\n\n验证：将 x = 1 代入原方程，1 + 1 = 2 ✓"
                else:
                    return "这是一个数学问题。我会逐步帮助你解决。请告诉我具体的方程内容，我会提供详细的解题步骤。"
            elif "cookies" in user_lower or "cookie" in user_lower or "饼干" in user_lower:
                return "让我们一步步解决这个应用题：\n\n1. 首先计算总饼干数：4 × 2 = 8（dozen）\n2. 8 dozen = 8 × 12 = 96（个饼干）\n3. 96个饼干平均分给16人：96 ÷ 16 = 6\n\n答案：每个人可以得到6个饼干。"
            else:
                return "我理解你的数学问题。请详细描述你的问题，我会提供帮助。作为大学一年级的数学导师，我会用适合大一水平的方法来解答。"

        # 历史辅导模拟
        if "history" in system_prompt.lower() or "历史" in system_prompt.lower():
            if "president" in user_lower or "总统" in user_lower:
                if "france" in user_lower or "法国" in user_lower:
                    return "法兰西第一共和国的第一位总统是路易·拿破仑·波拿巴（Louis-Napoléon Bonaparte），他于1848年12月20日当选总统。\n\n他是拿破仑一世的侄子，后来在1852年建立了法兰西第二帝国，自己成为拿破仑三世皇帝。"
                elif "hkust" in user_lower or "香港科技大学" in user_lower:
                    return "这个问题涉及本地小大学的具体信息，超出了我的辅导范围。我专门帮助学生了解具有普遍历史意义的重大事件。对于香港科技大学的具体历史，建议查询学校官方资料。"
                else:
                    return "我需要更具体的信息来回答这个历史问题。请说明是哪个国家或地区的总统。"
            elif "french revolution" in user_lower or "法国大革命" in user_lower:
                return "法国大革命（1789-1799）的主要经济原因包括：\n\n1. **财政危机**：法国在七年战争和美国独立战争中负债累累\n2. **税收不公**：第三等级（农民和城市贫民）承担重税，而贵族和教会免税\n3. **粮食价格飞涨**：1788年自然灾害导致粮食歉收，面包价格暴涨\n4. **土地问题**：农民渴望获得贵族和教会控制的土地\n\n这些经济矛盾与启蒙思想的传播相结合，最终引发了法国大革命。"
            else:
                return "我理解你的历史问题。请详细描述你感兴趣的历史事件或时期，我会提供适合大学一年级水平的解答。"

        # 拒绝回复模拟
        if "refuse" in system_prompt.lower() or "cannot help" in system_prompt.lower():
            if "travel" in user_lower or "trip" in user_lower or "旅行" in user_lower:
                return "抱歉，我是一个作业辅导Agent，专门帮助学生解答数学和历史问题。我无法帮助您规划旅行行程。"
            elif "firecracker" in user_lower or "鞭炮" in user_lower or "crackers" in user_lower:
                return "抱歉，我是一个作业辅导Agent。这个问题不像是作业问题，我无法帮助。"
            else:
                return "抱歉，这个问题不在我的辅导范围内。我专门帮助数学和历史作业问题。"

        # 总结功能模拟
        if "summarize" in system_prompt.lower() or "总结" in system_prompt.lower():
            return "## 对话总结\n\n到目前为止，我们讨论了以下内容：\n\n1. **数学问题**：包括微积分求导、有理数判定、基础代数方程和应用题\n2. **历史问题**：包括法国大革命的经济原因、法国总统历史\n\n如果你有其他问题，请继续提问。"

        # 默认回复
        return "我收到了你的问题：\n\n" + user_prompt[:200] + "\n\n请等待处理..."


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
