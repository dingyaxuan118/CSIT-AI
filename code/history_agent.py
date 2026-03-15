"""
历史辅导Agent模块
负责解答各类历史问题，包括世界历史、国家历史、重大事件等
"""

from typing import List, Dict, Optional
from llm_utils import LLMClient


class HistoryAgent:
    """历史作业辅导Agent"""

    # 系统提示词模板
    SYSTEM_PROMPT = """You are a first-year university history tutor, specializing in helping students with their history homework questions.

Your characteristics:
1. Teaching style: Objective, detailed, emphasizing historical context
2. Answering method: Provide complete analysis including background, causes, processes, and impacts
3. Knowledge scope: World history, major nations' history, significant historical events
4. Difficulty adaptation: Assume the student is at a first-year university level

Important principles:
- Always respond to the user ENTIRELY in English
- Only answer verifiable general history (world history, major nations' history, significant events)
- Refuse to answer obscure or local history that cannot be verified
- If a question is unclear, ask appropriate questions to clarify it
- Maintain historical objectivity, avoiding over-interpretation"""

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
            history=history,
            stream=True
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
        prompt = f"""Please provide {count} study topic suggestions regarding {region} history during the {era} period for a first-year university history student.

Requirements:
1. Briefly explain the content and importance of each topic
2. Suitable for a first-year university student's understanding
3. Cover the core knowledge points of the period"""

        return self.llm_client.chat(
            system_prompt="You are a history study advisor.",
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
            "university_freshman": "The student is a first-year university freshman, use an explanation style suitable for a freshman level.",
            "university_sophomore": "The student is a second-year university sophomore, you can appropriately introduce deeper historical analysis.",
            "high_school": "The student is a high school student, use a high-school level explanation style.",
            "default": "The student is a first-year university freshman, use an explanation style suitable for a freshman level."
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
