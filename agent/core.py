from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_community.chat_models import ChatOpenAI
import logging
import streamlit as st  
from datetime import datetime
import pytz  


logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler()
    ]
)

# Custom log function with Pakistan time
def log_with_local_time(message, level="info", data=None):
    pakistan_tz = pytz.timezone("Asia/Karachi")
    now = datetime.now(pakistan_tz).strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"{now} - {message}"
    if data:
        full_message += f": {data}"
    if level == "info":
        logging.info(full_message)
    elif level == "error":
        logging.error(full_message)

template = """
You are a daily reflection and planning assistant. Your goal is to:
1. Reflect on the user's journal and dream input
2. Interpret the user's emotional and mental state
3. Understand their intention and 3 priorities
4. Generate a practical, energy-aligned strategy for their day

INPUT:
Morning Journal: {journal}
Intention: {intention}
Dream: {dream}
Top 3 Priorities: {priorities}

OUTPUT:
1. Inner Reflection Summary
2. Dream Interpretation Summary
3. Energy/Mindset Insight
4. Suggested Day Strategy (time-aligned tasks)
"""

# Setup the prompt
prompt = PromptTemplate.from_template(template)

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)


chain = prompt | llm

# This function is used by app.py
def generate_response(journal, intention, dream, priorities):
    inputs = {
        "journal": journal,
        "intention": intention,
        "dream": dream,
        "priorities": priorities
    }

    log_with_local_time("Received user inputs")
    log_with_local_time("Inputs", data=inputs)

    try:
        response = chain.invoke(inputs)
        text = response.content if hasattr(response, 'content') else response
        log_with_local_time("LLM Response", data=text)
    except Exception as e:
        log_with_local_time("Error generating response", level="error", data=str(e))
        raise e

    return {
        "reflection": text.split("4.")[0],
        "strategy": "4." + text.split("4.")[1] if "4." in text else ""
    }
