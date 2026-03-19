"""
SmartTutor - 智能作业辅导Agent主程序
基于Streamlit的Web界面

功能：
- 多轮对话辅导
- 数学、历史、经济、化学问题解答
- 智能护栏系统
- 对话总结功能
"""

import streamlit as st
import sys
import os

# 将当前目录添加到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入自定义模块
from llm_utils import get_llm_client, LLMClient
from guardrails import Guardrails, IntentCategory, create_guardrails
from math_agent import MathAgent, create_math_agent
from history_agent import HistoryAgent, create_history_agent
from economics_agent import EconomicsAgent, create_economics_agent
from chemistry_agent import ChemistryAgent, create_chemistry_agent


# ==================== 页面配置 ====================
st.set_page_config(
    page_title="SmartTutor - Intelligent Homework Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== 样式设置 ====================
st.markdown("""
<style>
    /* 主标题样式 */
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1rem;
    }

    /* 欢迎消息样式 */
    .welcome-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* 聊天消息样式 */
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }

    .chat-message.user {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
    }

    .chat-message.assistant {
        background-color: #f3e5f5;
        border-left: 4px solid #7b1fa2;
    }

    .chat-message.system {
        background-color: #fff3e0;
        border-left: 4px solid #f57c00;
        font-style: italic;
    }

    /* 调试信息样式 */
    .debug-info {
        background-color: #263238;
        color: #aed581;
        padding: 1rem;
        border-radius: 5px;
        font-family: monospace;
        font-size: 0.85rem;
    }

    /* 状态指示器 */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }

    .status-accept { background-color: #4caf50; }
    .status-reject { background-color: #f44336; }
</style>
""", unsafe_allow_html=True)


# ==================== 会话状态初始化 ====================
def init_session_state():
    """初始化会话状态"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "api_source" not in st.session_state:
        st.session_state.api_source = "modelscope"  # 默认使用modelscope模式

    if "show_debug" not in st.session_state:
        st.session_state.show_debug = False

    if "user_level" not in st.session_state:
        st.session_state.user_level = "university_freshman"


# ==================== 组件函数 ====================
def render_sidebar():
    """渲染侧边栏"""
    st.sidebar.title("⚙️ Settings")

    # API来源选择
    api_source = st.sidebar.selectbox(
        "API Source",
        ["modelscope", "openai", "azure", "hkust"],
        index=0,
        help="Select the LLM API source to use."
    )
    st.session_state.api_source = api_source

    # 用户年级设置
    user_level = st.sidebar.selectbox(
        "My Grade",
        ["university_freshman", "university_sophomore", "high_school"],
        index=0,
        format_func=lambda x: {
            "university_freshman": "University Freshman",
            "university_sophomore": "University Sophomore",
            "high_school": "High School Student"
        }.get(x, x)
    )
    st.session_state.user_level = user_level

    # 调试开关
    show_debug = st.sidebar.checkbox("Show Debug Info", value=True)
    st.session_state.show_debug = show_debug

    # 重置对话
    if st.sidebar.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.rerun()

    # 帮助信息
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 📖 Instructions

    1. **Supported Subjects**: Math, History, Economics, Chemistry
    2. **How to ask**: Just enter your homework question directly
    3. **Special Features**:
       - Type "summarize" to summarize the conversation
       - Type "exercises" to get practice questions
    4. **Note**:
       - Non-academic topics like travel or entertainment will be rejected
       - Highly obscure or localized knowledge is out of scope
    """)


def render_header():
    """渲染页面头部"""
    st.markdown("""
    <div class="welcome-message">
        <h1>🎓 SmartTutor</h1>
        <p>Your personal Math, History, Economics, and Chemistry homework assistant</p>
        <p style="font-size: 0.9rem; opacity: 0.9;">Designed for University Freshmen | Secured by Smart Guardrails</p>
    </div>
    """, unsafe_allow_html=True)


def render_chat_history():
    """渲染聊天历史"""
    for msg in st.session_state.messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        debug_info = msg.get("debug", None)

        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"**You**: {content}")
        elif role == "assistant":
            with st.chat_message("assistant", avatar="🎓"):
                st.markdown(content)

                # 显示调试信息（如果开启）
                if debug_info and st.session_state.show_debug:
                    st.markdown("---")
                    st.markdown(f'<div class="debug-info">🔍 Debug Info: {debug_info}</div>',
                              unsafe_allow_html=True)
        elif role == "system":
            with st.chat_message("system", avatar="ℹ️"):
                st.markdown(content)


def process_user_input(user_input: str):
    """
    处理用户输入的核心逻辑

    Args:
        user_input: 用户输入
    Returns:
        tuple: (response, debug_info)
    """
    # 获取LLM客户端
    llm_client = get_llm_client(st.session_state.api_source)

    # 创建护栏系统
    guardrails = create_guardrails(llm_client)

    # 步骤1：验证输入
    is_valid, error_msg = guardrails.validate_input(user_input)
    if not is_valid:
        return f"❌ {error_msg}", "Input Validation Failed"

    # 步骤2：快速检查（基于关键词）
    quick_category, quick_reason = guardrails.quick_check(user_input)

    # 步骤3：LLM分类（更准确）
    llm_category = guardrails.classify_intent(user_input)

    # 优先使用LLM分类结果
    final_category = llm_category if llm_category != IntentCategory.UNKNOWN else quick_category

    # 调试信息
    debug_info = f"Quick Check: {quick_category.value} ({quick_reason}) | LLM Classification: {final_category.value}"

    # 步骤4：路由和处理
    response = ""

    # 根据分类结果进行处理
    if final_category == IntentCategory.MATH_HOMEWORK:
        # 数学问题
        math_agent = create_math_agent(llm_client)
        response = math_agent.answer(
            question=user_input,
            history=st.session_state.messages,
            user_level=st.session_state.user_level
        )

    elif final_category == IntentCategory.HISTORY_HOMEWORK:
        # 历史问题
        history_agent = create_history_agent(llm_client)
        response = history_agent.answer(
            question=user_input,
            history=st.session_state.messages,
            user_level=st.session_state.user_level
        )

    elif final_category == IntentCategory.ECONOMICS_HOMEWORK:
        # 经济问题
        economics_agent = create_economics_agent(llm_client)
        response = economics_agent.answer(
            question=user_input,
            history=st.session_state.messages,
            user_level=st.session_state.user_level
        )

    elif final_category == IntentCategory.CHEMISTRY_HOMEWORK:
        # 化学问题
        chemistry_agent = create_chemistry_agent(llm_client)
        response = chemistry_agent.answer(
            question=user_input,
            history=st.session_state.messages,
            user_level=st.session_state.user_level
        )

    elif final_category == IntentCategory.SUMMARY_REQUEST:
        # 总结请求
        summary_prompt = """Please summarize the main points of the following conversation:"""
        conversation = "\n".join([
            f"{msg['role']}: {msg['content'][:200]}"
            for msg in st.session_state.messages
        ])
        response = llm_client.chat(
            system_prompt="You are a conversation summary assistant. Please summarize the key points of the conversation concisely entirely in English.",
            user_prompt=f"{summary_prompt}\n\n{conversation}",
            stream=True
        )

    elif final_category == IntentCategory.OFF_TOPIC:
        # 离题内容
        response = guardrails.get_rejection_message(IntentCategory.OFF_TOPIC, quick_reason)

    elif final_category == IntentCategory.OBSCURE_SCOPE:
        # 冷门知识
        response = guardrails.get_rejection_message(IntentCategory.OBSCURE_SCOPE, quick_reason)

    elif final_category == IntentCategory.DANGEROUS:
        # 危险内容
        response = guardrails.get_rejection_message(IntentCategory.DANGEROUS, quick_reason)

    else:
        # 未知类型，尝试默认处理
        response = "Sorry, I couldn't understand your question. Please try asking in the form of a homework problem, for example:\n- Math: 'How to solve x+1=2?'\n- History: 'What were the causes of the French Revolution?'\n- Economics: 'How do supply and demand affect prices?'\n- Chemistry: 'What is the chemical formula for water?'"

    return response, debug_info


def main():
    """主函数"""
    # 初始化
    init_session_state()

    # 渲染界面
    render_sidebar()
    render_header()

    # 显示欢迎消息（首次访问）
    if not st.session_state.messages:
        st.info("👋 Welcome to SmartTutor! Please enter your math, history, economics, or chemistry homework question below.")

    # 渲染聊天历史
    render_chat_history()

    # 聊天输入框
    user_input = st.chat_input("Please enter your homework question...")

    if user_input:
        # 立即显示用户消息
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"**You**: {user_input}")

        # 系统处理并获取流式或普通响应
        response_data, debug_info = process_user_input(user_input)

        # 渲染助手响应
        with st.chat_message("assistant", avatar="🎓"):
            # 如果 response_data 是生成器（即流式内容）
            if hasattr(response_data, '__iter__') and not isinstance(response_data, str):
                full_response = st.write_stream(response_data)
            else:
                st.markdown(response_data)
                full_response = response_data
            
            if debug_info and st.session_state.show_debug:
                st.markdown("---")
                st.markdown(f'<div class="debug-info">🔍 Debug Info: {debug_info}</div>',
                            unsafe_allow_html=True)

        # 将双方对话存入历史记录，供刷新后渲染
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "debug": debug_info
        })


# ==================== 程序入口 ====================
if __name__ == "__main__":
    main()
