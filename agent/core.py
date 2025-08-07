from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_community.chat_models import ChatOpenAI
import logging
import os  # ✅ Only added this to use environment variable

# Setup logging to file and terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler()
    ]
)

# Define the prompt template
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

# ✅ Read OpenRouter API key securely from environment variable
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    api_key=os.getenv("OPENROUTER_API_KEY"),
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
