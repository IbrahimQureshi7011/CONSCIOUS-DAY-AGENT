from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_community.chat_models import ChatOpenAI
import logging
import streamlit as st  
from datetime import datetime
import pytz  # added for timezone support

# Setup logging with local timezone (Asia/Karachi)
class PakistanTimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        pakistan_tz = pytz.timezone("Asia/Karachi")
        dt = datetime.fromtimestamp(record.created, pakistan_tz)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.isoformat()

formatter = PakistanTimeFormatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler("agent.log")
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, stream_handler]
)

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

# Create chain
chain = prompt | llm

# This function is used by app.py
def generate_response(journal, intention, dream, priorities):
    inputs = {
        "journal": journal,
        "intention": intention,
        "dream": dream,
        "priorities": priorities
    }

    logging.info("Received user inputs")
    logging.info(inputs)

    try:
        response = chain.invoke(inputs)
        text = response.content if hasattr(response, 'content') else response
        logging.info("LLM Response:\n%s", text)
    except Exception as e:
        logging.error("Error generating response: %s", str(e))
        raise e

    return {
        "reflection": text.split("4.")[0],
        "strategy": "4." + text.split("4.")[1] if "4." in text else ""
    }
