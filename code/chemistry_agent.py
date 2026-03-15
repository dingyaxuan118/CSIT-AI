"""
化学辅导Agent模块
负责解答各类化学问题，包括有机化学、无机化学、物理化学等
"""

from typing import List, Dict, Optional
from llm_utils import LLMClient


class ChemistryAgent:
    """化学作业辅导Agent"""

    # 系统提示词模板
    SYSTEM_PROMPT = """你是一位大学一年级的化学助教，专门帮助学生解答化学作业问题。

你的特点：
1. 教学风格：耐心、详细、循序渐进
2. 解释方法：强调化学原理和反应机制
3. 知识范围：有机化学基础、无机化学、物理化学入门、元素周期表、化学反应
4. 难度适配：假设学生是大学一年级水平

重要原则：
- 如果问题超出大学一年级范围，请明确告知学生
- 如果是基础概念问题，可以直接解释
- 如果是复杂问题，请分步骤讲解
- 使用清晰的化学术语和结构式
- 适当使用化学方程式和例子来解释反应"""

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
        prompt = f"""请为大学一年级学生生成{count}道关于"{topic}"的化学练习题，难度为{difficulty}。

要求：
1. 包含题目和详细解答
2. 难度适中，适合大一学生
3. 涵盖该主题的核心知识点"""

        return self.llm_client.chat(
            system_prompt="你是一位化学练习题生成专家。",
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
            "university_freshman": "学生是大学一年级新生，使用适合大一水平的讲解方式，侧重基础概念和原理。",
            "university_sophomore": "学生是大学二年级学生，可以适当引入更深入的反应机理和复杂概念。",
            "high_school": "学生是高中生，使用高中水平的讲解方式，侧重基本化学概念解释。",
            "default": "学生是大学一年级新生，使用适合大一水平的讲解方式，侧重基础概念和原理。"
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
