"""
化学辅导Agent模块
负责解答各类化学问题，包括有机化学、无机化学、物理化学等
"""

from typing import List, Dict, Optional
from llm_utils import LLMClient


class ChemistryAgent:
    """化学作业辅导Agent"""

    # 系统提示词模板
    SYSTEM_PROMPT = """You are a first-year university chemistry teaching assistant, specialized in helping students with chemistry homework questions.

Your characteristics:
1. Teaching style: Patient, detailed, step-by-step
2. Explanation method: Emphasize chemical principles and reaction mechanisms
3. Knowledge scope: Basic Organic Chemistry, Inorganic Chemistry, Introduction to Physical Chemistry, periodic table, chemical reactions
4. Difficulty adaptation: Assume the student is at a first-year university level

Important principles:
- Always respond to the user ENTIRELY in English
- If a question is beyond the scope of a first-year university student, please clearly inform the student
- If it is a basic conceptual question, you can explain it directly
- If it is a complex question, please explain it step-by-step
- Use clear chemical terminology and structural formulas
- Appropriately use chemical equations and examples to explain reactions"""

    def __init__(self, llm_client: LLMClient):
        """
        初始化化学Agent

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
        解答化学问题

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
1. 先解释相关化学概念
2. 提供分析思路
3. 给出详细解释（如果适用）
4. 给出最终结论
5. 如果有化学反应方程式，请一并写出"""

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
            topic: 主题（如"有机化学"、"化学反应"等）
            difficulty: 难度（easy/medium/hard）
            count: 题目数量

        Returns:
            练习题文本
        """
        prompt = f"""Please generate {count} chemistry practice questions on the topic "{topic}" for a first-year university student, with a difficulty of {difficulty}.

Requirements:
1. Include both the questions and detailed answers
2. Moderate difficulty, suitable for university freshmen
3. Covers the core knowledge points of the topic"""

        return self.llm_client.chat(
            system_prompt="You are a chemistry practice question generation expert.",
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
            "university_freshman": "The student is a first-year university freshman, use an explanation style suitable for a freshman level, focusing on basic concepts and principles.",
            "university_sophomore": "The student is a second-year university sophomore, you can appropriately introduce deeper reaction mechanisms and complex concepts.",
            "high_school": "The student is a high school student, use a high-school level explanation style, focusing on basic chemical conceptual explanations.",
            "default": "The student is a first-year university freshman, use an explanation style suitable for a freshman level, focusing on basic concepts and principles."
        }
        return level_prompts.get(user_level, level_prompts["default"])


def create_chemistry_agent(llm_client: LLMClient) -> ChemistryAgent:
    """
    创建化学Agent的工厂函数

    Args:
        llm_client: LLM客户端

    Returns:
        ChemistryAgent实例
    """
    return ChemistryAgent(llm_client)
