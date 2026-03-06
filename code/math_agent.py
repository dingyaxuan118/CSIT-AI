"""
数学辅导Agent模块
负责解答各类数学问题，包括代数、微积分、线性代数等
"""

from typing import List, Dict, Optional
from llm_utils import LLMClient


class MathAgent:
    """数学作业辅导Agent"""

    # 系统提示词模板
    SYSTEM_PROMPT = """你是一位大学一年级的数学助教，专门帮助学生解答数学作业问题。

你的特点：
1. 教学风格：耐心、详细、循序渐进
2. 解题方法：强调步骤和思路，而非直接给出答案
3. 知识范围：微积分I、线性代数I、基础代数、概率论入门
4. 难度适配：假设学生是大学一年级水平

重要原则：
- 如果问题超出大学一年级范围，请明确告知学生
- 如果是简单问题，可以直接给出解答
- 如果是复杂问题，请分步骤讲解
- 对于计算题，请展示完整计算过程
- 使用清晰的数学符号和格式"""

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
            history=history
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
        prompt = f"""请为大学一年级学生生成{count}道关于"{topic}"的练习题，难度为{difficulty}。

要求：
1. 包含题目和详细解答
2. 难度适中，适合大一学生
3. 涵盖该主题的核心知识点"""

        return self.llm_client.chat(
            system_prompt="你是一位数学练习题生成专家。",
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
            "university_sophomore": "学生是大学二年级学生，可以适当引入更深入的概念。",
            "high_school": "学生是高中生，使用高中水平的讲解方式。",
            "default": "学生是大学一年级新生，使用适合大一水平的讲解方式。"
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
