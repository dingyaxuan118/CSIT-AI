"""
经济辅导Agent模块
负责解答各类经济学问题，包括微观经济学、宏观经济学等
"""

from typing import List, Dict, Optional
from llm_utils import LLMClient


class EconomicsAgent:
    """经济作业辅导Agent"""

    # 系统提示词模板
    SYSTEM_PROMPT = """你是一位大学一年级的经济学助教，专门帮助学生解答经济作业问题。

你的特点：
1. 教学风格：耐心、详细、循序渐进
2. 解释方法：强调经济原理和逻辑分析
3. 知识范围：微观经济学基础、宏观经济学入门、供求关系、市场机制、经济指标
4. 难度适配：假设学生是大学一年级水平

重要原则：
- 如果问题超出大学一年级范围，请明确告知学生
- 如果是基础概念问题，可以直接解释
- 如果是复杂问题，请分步骤讲解
- 使用清晰的经济学术语和实际案例
- 适当使用图表和例子来解释经济现象"""

    def __init__(self, llm_client: LLMClient):
        """
        初始化经济Agent

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
        解答经济问题

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
1. 先解释相关经济概念
2. 提供分析框架
3. 给出详细解释（如果适用）
4. 给出最终结论
5. 如果有实际经济案例，请一并说明"""

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
            topic: 主题（如"供求关系"、"通货膨胀"等）
            difficulty: 难度（easy/medium/hard）
            count: 题目数量

        Returns:
            练习题文本
        """
        prompt = f"""请为大学一年级学生生成{count}道关于"{topic}"的经济学练习题，难度为{difficulty}。

要求：
1. 包含题目和详细解答
2. 难度适中，适合大一学生
3. 涵盖该主题的核心知识点"""

        return self.llm_client.chat(
            system_prompt="你是一位经济学练习题生成专家。",
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
            "university_sophomore": "学生是大学二年级学生，可以适当引入更深入的分析方法和模型。",
            "high_school": "学生是高中生，使用高中水平的讲解方式，侧重基本经济概念解释。",
            "default": "学生是大学一年级新生，使用适合大一水平的讲解方式，侧重基础概念和原理。"
        }
        return level_prompts.get(user_level, level_prompts["default"])


def create_economics_agent(llm_client: LLMClient) -> EconomicsAgent:
    """
    创建经济Agent的工厂函数

    Args:
        llm_client: LLM客户端

    Returns:
        EconomicsAgent实例
    """
    return EconomicsAgent(llm_client)
