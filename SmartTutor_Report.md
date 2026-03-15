# SmartTutor: Intelligent Homework Assistant Agent

## 1. System Architecture & Components

The SmartTutor system is modularly designed, separating the user interface, safety logic, domain knowledge, and API interactions.

* **Main Application (`app.py`)**: The Streamlit entry point. It manages session state, renders the sidebar settings (API Provider, Grade Level, Instructions), handles the chat UI, dynamically delegates user input to the correct processing logic, and streams the output directly to the screen.
* **Intelligent Guardrails (`guardrails.py`)**: The system's primary safety and routing mechanism. It features a two-step intent classification system:
  1. A fast keyword-based pre-check (detecting dangerous, off-topic, obscure, or subject-specific keywords).
  2. An LLM-powered context classification to accurately route questions to specific domains (Math, History, Economics, Chemistry, or Conversation Summary). It actively blocks non-academic or inappropriate questions.
* **Domain-Specific Agents (`math_agent.py`, `history_agent.py`, `economics_agent.py`, `chemistry_agent.py`)**: Handlers tailored for distinct academic fields. Each agent adopts a specific persona and context to ensure answers are structurally appropriate for the subject.
* **LLM Utility Engine (`llm_utils.py`)**: A centralized wrapper to manage Large Language Model API calls. It supports multiple API providers (such as standard OpenAI, Azure OpenAI, and HKUST GenAI) using Python generators to manage Server-Sent Events (SSE) for modern UI text streaming.

## 2. Instructions on Running the Agent

```bash
cd code
pip install streamlit openai
streamlit run app.py
```

## 3. Examples

History question (accepted): 

![image-20260315205705328](./Report.assets/image-20260315205705328.png)

Math question (accepted):

![image-20260315205932426](./Report.assets/image-20260315205932426.png)

Out-of-scope question (rejected):

![image-20260315210022565](./Report.assets/image-20260315210022565.png)

Non-homework question (rejected):

![image-20260315210102975](./Report.assets/image-20260315210102975.png)

Conversation summary request:

![image-20260315210146706](./Report.assets/image-20260315210146706.png)