"""
历史辅导Agent模块
负责解答各类历史问题，包括世界历史、国家历史、重大事件等
"""

from typing import List, Dict, Optional
from llm_utils import LLMClient


class HistoryAgent:
    """历史作业辅导Agent"""

    # 系统提示词模板
    SYSTEM_PROMPT = """你是一位大学一年级的历史导师，专门帮助学生解答历史作业问题。

你的特点：
1. 教学风格：客观、详实、注重历史背景
2. 解答方法：提供背景、原因、过程、影响等完整分析
3. 知识范围：世界历史、主要国家历史、重大历史事件
4. 难度适配：假设学生是大学一年级水平

重要原则：
- 只回答有据可查的通用历史（世界历史、大国历史、重大事件）
- 拒绝回答无法验证的本地冷门历史
- 如果问题不明确，适当询问以明确问题
- 保持历史客观性，避免过度解读"""

    def __init__(self, llm_client: LLMClient):
        """
        初始化历史Agent

        Args:
            llm_client: LLM客户端实例
        """
        self.llm_client = llm_client

    def answer(
        self,
        question: str,
        history: Optional[List[Dict[str, str]]] = None,
        user_level: str = "university_freshman"
    ) -> str:
        """
        解答历史问题

        Args:
            question: 用户问题
            history: 对话历史
            user_level: 用户年级水平

        Returns:
            解答文本
        """
        # 构建上下文感知的提示词
        level_prompt = self._get_level_prompt(user_level)

        full_prompt = f"""{self.SYSTEM_PROMPT}

{level_prompt}

用户问题：{question}

请按照以下格式回答：
1. 简要回答问题核心
2. 提供历史背景
3. 分析原因和影响
4. 如有需要，给出进一步学习的建议"""

        return self.llm_client.chat(
            system_prompt=full_prompt,
            user_prompt=question,
            history=history
        )

    def generate_topics(
        self,
        era: str = "modern",
        region: str = "world",
        count: int = 3
    ) -> str:
        """
        生成历史学习主题建议

        Args:
            era: 时代（如"古代"、"近代"、"现代"）
            region: 地区（如"世界"、"欧洲"、"亚洲"）
            count: 主题数量

        Returns:
            主题建议文本
        """
        prompt = f"""请为大学一年级历史学生提供{count}个关于{era}时期{region}历史的学习主题建议。

要求：
1. 每个主题简要说明内容和重要性
2. 适合大一学生理解
3. 涵盖该时期的核心知识点"""

        return self.llm_client.chat(
            system_prompt="你是一位历史学习顾问。",
            user_prompt=prompt,
            temperature=0.8
        )

    def _get_level_prompt(self, user_level: str) -> str:
        """
        获取年级适配提示词

        Args:
            user_level: 年级水平

        Returns:
            适配提示词
        """
        level_prompts = {
            "university_freshman": "学生是大学一年级新生，使用适合大一水平的讲解方式。",
            "university_sophomore": "学生是大学二年级学生，可以适当引入更深入的历史分析。",
            "high_school": "学生是高中生，使用高中水平的讲解方式。",
            "default": "学生是大学一年级新生，使用适合大一水平的讲解方式。"
        }
        return level_prompts.get(user_level, level_prompts["default"])


def create_history_agent(llm_client: LLMClient) -> HistoryAgent:
    """
    创建历史Agent的工厂函数

    Args:
        llm_client: LLM客户端

    Returns:
        HistoryAgent实例
    """
    return HistoryAgent(llm_client)
