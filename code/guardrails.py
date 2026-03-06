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
    FINANCE_HOMEWORK = "FINANCE_HOMEWORK" # 金融作业
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
        classification_prompt = """你是一个意图分类系统。请分析用户的输入并将其分类为以下类别之一：

- MATH_HOMEWORK: 数学作业问题（计算、证明、方程、微积分、线性代数等）
- HISTORY_HOMEWORK: 历史作业问题（重大历史事件、人物、时期、世界历史等）
- FINANCE_HOMEWORK: 金融作业问题（投资、风险管理、金融市场、财务报表等）
- ECONOMICS_HOMEWORK: 经济学作业问题（供求关系、宏观经济、微观经济、市场机制等）
- CHEMISTRY_HOMEWORK: 化学作业问题（化学反应、分子结构、元素周期表、有机化学等）
- SUMMARY_REQUEST: 请求总结之前的对话
- OFF_TOPIC: 离题内容（旅行、娱乐、日常生活建议等）
- OBSCURE_SCOPE: 冷门/本地知识（具体的小大学、本地小店等无法验证的内容）
- DANGEROUS: 危险内容（暴力、违法等）

请只输出类别名称，不要输出其他内容。"""

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
                return (IntentCategory.DANGEROUS, f"检测到危险关键词: {keyword}")

        # 检查离题内容
        for keyword in self.OFF_TOPIC_KEYWORDS:
            if keyword in user_lower:
                return (IntentCategory.OFF_TOPIC, f"检测到离题关键词: {keyword}")

        # 检查冷门知识
        for keyword in self.OBSCURE_KEYWORDS:
            if keyword in user_lower:
                return (IntentCategory.OBSCURE_SCOPE, f"检测到冷门知识关键词: {keyword}")

        # 检查总结请求
        if any(word in user_lower for word in ["summarize", "总结", "摘要", "概括"]):
            if any(word in user_lower for word in ["conversation", "对话", "我们", "刚才"]):
                return (IntentCategory.SUMMARY_REQUEST, "检测到总结请求")

        # 检查学科关键词
        math_keywords = ["derivative", "integral", "equation", "solve", "calculate",
                        "calculus", "algebra", "matrix", "probability",
                        "导数", "积分", "方程", "计算", "微积分", "代数", "矩阵"]
        history_keywords = ["history", "president", "revolution", "war", "empire",
                          "history", "ancient", "modern", "century",
                          "历史", "总统", "革命", "战争", "帝国", "古代", "现代"]
        finance_keywords = ["stock", "bond", "investment", "portfolio", "dividend",
                          "financial", "market", "trading", "interest", "risk",
                          "股票", "债券", "投资", "股息", "金融", "市场", "交易", "利率", "风险"]
        economics_keywords = ["economics", "gdp", "inflation", "supply", "demand",
                            "macro", "micro", "trade", "currency", "fiscal",
                            "经济", "国内生产总值", "通货膨胀", "供给", "需求", "宏观", "微观", "贸易", "货币", "财政"]
        chemistry_keywords = ["chemistry", "chemical", "reaction", "molecule", "atom",
                            "element", "periodic", "organic", "inorganic", "bond",
                            "化学", "化学反应", "分子", "原子", "元素", "周期表", "有机", "无机"]

        for keyword in math_keywords:
            if keyword in user_lower:
                return (IntentCategory.MATH_HOMEWORK, f"检测到数学关键词: {keyword}")

        for keyword in history_keywords:
            if keyword in user_lower:
                return (IntentCategory.HISTORY_HOMEWORK, f"检测到历史关键词: {keyword}")

        for keyword in finance_keywords:
            if keyword in user_lower:
                return (IntentCategory.FINANCE_HOMEWORK, f"检测到金融关键词: {keyword}")

        for keyword in economics_keywords:
            if keyword in user_lower:
                return (IntentCategory.ECONOMICS_HOMEWORK, f"检测到经济关键词: {keyword}")

        for keyword in chemistry_keywords:
            if keyword in user_lower:
                return (IntentCategory.CHEMISTRY_HOMEWORK, f"检测到化学关键词: {keyword}")

        return (IntentCategory.UNKNOWN, "未检测到明确意图")

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
            return False, "输入不能为空"

        # 检查长度
        if len(user_input) > 2000:
            return False, "输入过长，请简化问题"

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
            IntentCategory.FINANCE_HOMEWORK,
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
            IntentCategory.OFF_TOPIC: "抱歉，我是一个作业辅导Agent，专门帮助学生解答数学、历史、金融、经济和化学问题。您的这个问题不在我的辅导范围内。",
            IntentCategory.OBSCURE_SCOPE: "抱歉，这个问题涉及较为冷门或本地化的知识，可能无法提供准确的信息。我专门帮助大学一年级的数学、历史、金融、经济和化学作业问题。",
            IntentCategory.DANGEROUS: "抱歉，我无法帮助处理这类内容。请专注于学业相关的问题。",
            IntentCategory.UNKNOWN: "抱歉，我无法理解您的问题。请尝试以作业问题的形式提问，例如：\n- 数学：'如何求导？'\n- 历史：'法国大革命的原因是什么？'\n- 金融：'什么是股票？'\n- 经济：'供给和需求如何影响价格？'\n- 化学：'水的化学式是什么？'"
        }

        base_message = messages.get(category, "抱歉，我无法帮助回答这个问题。")

        if reason:
            return f"{base_message}\n\n原因：{reason}"

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
