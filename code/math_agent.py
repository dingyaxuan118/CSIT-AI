"""
数学辅导Agent模块
负责解答各类数学问题，包括代数、微积分、线性代数等
"""

from typing import List, Dict, Optional
from llm_utils import LLMClient


class MathAgent:
    """数学作业辅导Agent"""

    # 系统提示词模板
    SYSTEM_PROMPT = """You are a first-year university math teaching assistant, specialized in helping students with math homework given.

Your characteristics:
1. Teaching style: Patient, detailed, step-by-step
2. Problem-solving approach: Emphasize steps and reasoning, not just giving the final answer
3. Knowledge scope: Calculus I, Linear Algebra I, Basic Algebra, Introduction to Probability
4. Difficulty adaptation: Assume the student is at a first-year university level

Important principles:
- Always respond to the user ENTIRELY in English
- If a question is beyond the scope of a first-year university student, please clearly inform the student
- If it is a simple question, you can give the answer directly
- If it is a complex question, please explain it step-by-step
- For calculation problems, show the complete calculation process
- Use clear mathematical symbols and formatting"""

    def __init__(self, llm_client: LLMClient):
        """
        初始化数学Agent

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
        解答数学问题

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
1. 先理解问题
2. 提供解题思路
3. 给出详细步骤（如果适用）
4. 给出最终答案
5. 如果有其他解法，请一并说明"""

        return self.llm_client.chat(
            system_prompt=full_prompt,
            user_prompt=question,
            history=history,
            stream=True
        )

    def generate_exercises(
        self,
        topic: str,
        difficulty: str = "medium",
        count: int = 3
    ) -> str:
        """
        生成练习题

        Args:
            topic: 主题（如"微积分"、"线性代数"等）
            difficulty: 难度（easy/medium/hard）
            count: 题目数量

        Returns:
            练习题文本
        """
        prompt = f"""Please generate {count} practice questions on the topic "{topic}" for a first-year university student, with a difficulty of {difficulty}.

Requirements:
1. Include both the questions and detailed answers
2. Moderate difficulty, suitable for university freshmen
3. Covers the core knowledge points of the topic"""

        return self.llm_client.chat(
            system_prompt="You are a mathematics practice question generation expert.",
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
            "university_sophomore": "The student is a second-year university sophomore, you can introduce deeper concepts when appropriate.",
            "high_school": "The student is a high school student, use a high-school level explanation style.",
            "default": "The student is a first-year university freshman, use an explanation style suitable for a freshman level."
        }
        return level_prompts.get(user_level, level_prompts["default"])


def create_math_agent(llm_client: LLMClient) -> MathAgent:
    """
    创建数学Agent的工厂函数

    Args:
        llm_client: LLM客户端

    Returns:
        MathAgent实例
    """
    return MathAgent(llm_client)
