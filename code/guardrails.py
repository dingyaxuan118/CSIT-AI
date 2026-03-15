"""
护栏模块（Guardrails）- 核心的可靠性保障
负责意图分类、范围检查、安全过滤
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum

# 意图分类枚举
class IntentCategory(Enum):
    """用户意图分类"""
    MATH_HOMEWORK = "MATH_HOMEWORK"      # 数学作业
    HISTORY_HOMEWORK = "HISTORY_HOMEWORK" # 历史作业
    ECONOMICS_HOMEWORK = "ECONOMICS_HOMEWORK" # 经济作业
    CHEMISTRY_HOMEWORK = "CHEMISTRY_HOMEWORK" # 化学作业
    SUMMARY_REQUEST = "SUMMARY_REQUEST"   # 总结请求
    OFF_TOPIC = "OFF_TOPIC"               # 离题（旅行、娱乐等）
    OBSCURE_SCOPE = "OBSCURE_SCOPE"       # 范围外（冷门本地知识）
    DANGEROUS = "DANGEROUS"               # 危险内容
    UNKNOWN = "UNKNOWN"                   # 未知


class Guardrails:
    """
    护栏系统类
    负责输入验证、意图分类、路由决策
    """

    # 离题关键词（用于快速检查）
    OFF_TOPIC_KEYWORDS = [
        "travel", "trip", "itinerary", "vacation", "holiday",
        "hotel", "flight", "booking", "tourist", "attraction",
        "movie", "film", "music", "game", "sports", "entertainment",
        "recipe", "cooking", "fashion", "beauty", "dating",
        "旅行", "旅游", "度假", "酒店", "机票", "预订",
        "电影", "音乐", "游戏", "运动", "娱乐", "美食", "时尚"
    ]

    # 危险关键词
    DANGEROUS_KEYWORDS = [
        "weapon", "bomb", "explosive", "firecracker", "drug",
        "hack", "crack", "illegal", "violence", "attack",
        "武器", "炸弹", "爆炸物", "鞭炮", "毒品", "黑客",
        "暴力", "攻击", "违法"
    ]

    # 冷门/本地知识关键词（需要拒绝的）
    OBSCURE_KEYWORDS = [
        "hkust library", "local university", "small college",
        "vending machine", "local cafe", "neighborhood",
        "本地大学", "小大学", "自动售货机", "本地咖啡店",
        "社区", "街道", "具体的小店"
    ]

    def __init__(self, llm_client=None):
        """
        初始化护栏系统

        Args:
            llm_client: LLM客户端实例
        """
        self.llm_client = llm_client

    def classify_intent(self, user_input: str) -> IntentCategory:
        """
        使用LLM进行意图分类

        Args:
            user_input: 用户输入

        Returns:
            IntentCategory枚举值
        """
        if not self.llm_client:
            return IntentCategory.UNKNOWN

        # 构建分类提示词
        classification_prompt = """You are an intent classification system. Please analyze the user's input and classify it into one of the following categories:

- MATH_HOMEWORK: Math homework questions (calculation, proof, equation, calculus, linear algebra, etc.)
- HISTORY_HOMEWORK: History homework questions (major historical events, figures, periods, world history, etc.)
- ECONOMICS_HOMEWORK: Economics homework questions (supply and demand, macroeconomics, microeconomics, market mechanisms, etc.)
- CHEMISTRY_HOMEWORK: Chemistry homework questions (chemical reactions, molecular structure, periodic table, organic chemistry, etc.)
- SUMMARY_REQUEST: Request to summarize the previous conversation
- OFF_TOPIC: Off-topic content (travel, entertainment, daily life advice, etc.)
- OBSCURE_SCOPE: Obscure/local knowledge (specific small colleges, local shops, etc. that cannot be verified)
- DANGEROUS: Dangerous content (violence, illegal activities, etc.)

Please output ONLY the category name, and nothing else."""

        try:
            result = self.llm_client.chat(
                system_prompt=classification_prompt,
                user_prompt=user_input,
                temperature=0.1,  # 低温度以获得更一致的分类
                max_tokens=50
            )

            # 解析分类结果
            result = result.strip().upper()
            for category in IntentCategory:
                if category.value in result:
                    return category

            return IntentCategory.UNKNOWN

        except Exception as e:
            print(f"分类错误: {e}")
            return IntentCategory.UNKNOWN

    def quick_check(self, user_input: str) -> Tuple[IntentCategory, str]:
        """
        快速检查（基于关键词的预筛选）

        Args:
            user_input: 用户输入

        Returns:
            (IntentCategory, 原因)元组
        """
        user_lower = user_input.lower()

        # 检查危险内容
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in user_lower:
                return (IntentCategory.DANGEROUS, f"Dangerous keyword detected: {keyword}")

        # 检查离题内容
        for keyword in self.OFF_TOPIC_KEYWORDS:
            if keyword in user_lower:
                return (IntentCategory.OFF_TOPIC, f"Off-topic keyword detected: {keyword}")

        # 检查冷门知识
        for keyword in self.OBSCURE_KEYWORDS:
            if keyword in user_lower:
                return (IntentCategory.OBSCURE_SCOPE, f"Obscure knowledge keyword detected: {keyword}")

        # 检查总结请求
        if any(word in user_lower for word in ["summarize", "总结", "摘要", "概括"]):
            if any(word in user_lower for word in ["conversation", "对话", "我们", "刚才"]):
                return (IntentCategory.SUMMARY_REQUEST, "Summary request detected")

        # 检查学科关键词
        math_keywords = ["derivative", "integral", "equation", "solve", "calculate",
                        "calculus", "algebra", "matrix", "probability",
                        "导数", "积分", "方程", "计算", "微积分", "代数", "矩阵"]
        history_keywords = ["history", "president", "revolution", "war", "empire",
                          "history", "ancient", "modern", "century",
                          "历史", "总统", "革命", "战争", "帝国", "古代", "现代"]
        economics_keywords = ["economics", "gdp", "inflation", "supply", "demand",
                            "macro", "micro", "trade", "currency", "fiscal",
                            "经济", "国内生产总值", "通货膨胀", "供给", "需求", "宏观", "微观", "贸易", "货币", "财政"]
        chemistry_keywords = ["chemistry", "chemical", "reaction", "molecule", "atom",
                            "element", "periodic", "organic", "inorganic", "bond",
                            "化学", "化学反应", "分子", "原子", "元素", "周期表", "有机", "无机"]

        for keyword in math_keywords:
            if keyword in user_lower:
                return (IntentCategory.MATH_HOMEWORK, f"Math keyword detected: {keyword}")

        for keyword in history_keywords:
            if keyword in user_lower:
                return (IntentCategory.HISTORY_HOMEWORK, f"History keyword detected: {keyword}")

        for keyword in economics_keywords:
            if keyword in user_lower:
                return (IntentCategory.ECONOMICS_HOMEWORK, f"Economics keyword detected: {keyword}")

        for keyword in chemistry_keywords:
            if keyword in user_lower:
                return (IntentCategory.CHEMISTRY_HOMEWORK, f"Chemistry keyword detected: {keyword}")

        return (IntentCategory.UNKNOWN, "No clear intent detected")

    def validate_input(self, user_input: str) -> Tuple[bool, str]:
        """
        验证用户输入是否有效

        Args:
            user_input: 用户输入

        Returns:
            (是否有效, 错误消息)元组
        """
        # 检查是否为空
        if not user_input or not user_input.strip():
            return False, "Input cannot be empty."

        # 检查长度
        if len(user_input) > 2000:
            return False, "Input is too long, please simplify your question."

        return True, ""

    def should_accept(self, category: IntentCategory) -> bool:
        """
        判断是否应该接受该类别的请求

        Args:
            category: 意图分类

        Returns:
            True表示接受，False表示拒绝
        """
        accepted_categories = [
            IntentCategory.MATH_HOMEWORK,
            IntentCategory.HISTORY_HOMEWORK,
            IntentCategory.ECONOMICS_HOMEWORK,
            IntentCategory.CHEMISTRY_HOMEWORK,
            IntentCategory.SUMMARY_REQUEST
        ]
        return category in accepted_categories

    def get_rejection_message(self, category: IntentCategory, reason: str = "") -> str:
        """
        生成拒绝回复

        Args:
            category: 意图分类
            reason: 拒绝原因

        Returns:
            拒绝消息文本
        """
        messages = {
            IntentCategory.OFF_TOPIC: "Sorry, I am a homework tutoring Agent specifically designed to help students with Math, History, Economics, and Chemistry problems. Your question is outside my tutoring scope.",
            IntentCategory.OBSCURE_SCOPE: "Sorry, this question involves relatively obscure or highly localized knowledge, and I might not be able to provide accurate information. I specialize in helping first-year university students with Math, History, Economics, and Chemistry homework problems.",
            IntentCategory.DANGEROUS: "Sorry, I cannot help process this type of content. Please focus on academic-related questions.",
            IntentCategory.UNKNOWN: "Sorry, I cannot understand your question. Please try asking in the form of a homework problem, for example:\n- Math: 'How do you calculate a derivative?'\n- History: 'What were the causes of the French Revolution?'\n- Economics: 'How do supply and demand affect prices?'\n- Chemistry: 'What is the chemical formula for water?'"
        }

        base_message = messages.get(category, "Sorry, I cannot help answer this question.")

        if reason:
            return f"{base_message}\n\nReason: {reason}"

        return base_message


def create_guardrails(llm_client=None) -> Guardrails:
    """
    创建护栏系统的工厂函数

    Args:
        llm_client: LLM客户端

    Returns:
        Guardrails实例
    """
    return Guardrails(llm_client)
