from typing import TypedDict
from vector_db import retrieve_policy
from langchain_groq import ChatGroq
from sqlalchemy import create_engine, text
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Get Groq API key from .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set")

# Create LLM
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    groq_api_key=GROQ_API_KEY
)

# Get database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

# Create database engine
engine = create_engine(DATABASE_URL)

# StateGraph
class AgentState(TypedDict):
    question:str
    route:str
    sql:str
    sql_result:str
    analysis:str
    recommendation:str
    policy_content:str
    #next_agent:str
    final_answer:str

def supervisor(state: AgentState):

    question = state["question"]

    prompt = f"""
    You are a routing supervisor for a Business Analytics and Decision Support system.

    User Question:
    {question}

    Choose exactly ONE route:

    SQL
    Use SQL when the user asks for:
    - sales
    - profit
    - revenue
    - products
    - regions
    - customers
    - quantities
    - trends
    - comparisons
    - database information

    RAG
    Use RAG when the user asks about:
    - company policies
    - pricing policy
    - discount policy
    - approval rules
    - business rules
    - procedures

    SQL_RAG
    Use SQL_RAG when the user asks for:
    - recommendations
    - what should we do
    - what action should we take
    - what strategy should we use
    - whether a business action is allowed based on current data
    - business decisions requiring both data and policy

    Return ONLY:
    SQL
    RAG
    or
    SQL_RAG
    """

    response = llm.invoke(prompt)

    route = response.content.strip().upper()

    if route not in ["SQL", "RAG", "SQL_RAG"]:
        route = "SQL"

    return {"route": route}

def sql_agent(state: AgentState):

    question = state["question"]

    prompt = f"""
    You are a PostgreSQL query generator.

    Convert the user's question into a PostgreSQL query.

    Database table:
    sales

    Columns:
    order_id
    order_date
    product
    category
    region
    quantity
    sales
    profit
    customer

    Rules:
    - Generate only SQL.
    - Do not explain the SQL.
    - Use PostgreSQL syntax.
    - Only use the table and columns provided.

    QUESTION:
    {question}
    """

    response = llm.invoke(prompt)

    sql = response.content.strip()

    # Remove markdown code fences
    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    sql_lower = sql.lower()

    # Block dangerous commands
    forbidden_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "create",
        "grant",
        "revoke"
    ]

    # Only allow SELECT queries
    if not sql_lower.startswith("select"):
        return {
            "sql": sql,
            "sql_result": "Invalid SQL generated."
        }

    # Check dangerous commands
    for key in forbidden_keywords:
        if key in sql_lower:
            return {
                "sql": sql,
                "sql_result": "Invalid SQL generated."
            }

    # Make sure query uses sales table
    if "sales" not in sql_lower:
        return {
            "sql": sql,
            "sql_result": "Invalid SQL generated."
        }

    # Execute query
    try:

        with engine.connect() as connection:

            result = connection.execute(text(sql))

            rows = result.fetchall()

            columns = result.keys()

            data = [
                dict(zip(columns, row))
                for row in rows
            ]

        return {
            "sql": sql,
            "sql_result": str(data)
        }

    except Exception as e:

        return {
            "sql": sql,
            "sql_result": f"Database error: {str(e)}"
        }
#This is where the LLM becomes a business analytics assistant rather than just a SQL generator.
# It receives user questions and sql result

def rag_agent(state: AgentState):

    question = state["question"]

    policy_context = retrieve_policy(question)

    return {
        "policy_context": policy_context
    }

def policy_answer_agent(state: AgentState):

    question = state["question"]
    policy_context = state.get("policy_context", "")

    prompt = f"""
    You are a Business Policy Assistant.

    User Question:
    {question}

    Relevant Company Policy:
    {policy_context}

    Answer the user's question using ONLY the policy information provided.

    Rules:
    - Return ONLY one sentence.
    - Give the specific answer.
    - Do not mention RAG.
    - Do not mention the policy document.
    - Do not show reasoning.
    - Do not invent information.

    Example:
    Question: Who can approve a discount above 25%?

    Answer: Discounts above 25% require approval from the CFO.
    """

    response = llm.invoke(prompt)

    return {
        "analysis": response.content.strip()
    }

def analytics_agent(state: AgentState):

    question = state["question"]
    sql_result = state["sql_result"]

    prompt = f"""
    User question: {question}

    Database result: {sql_result}

    Convert the database result into ONE simple sentence for the user in natural language.
    Rules:
    - Return ONLY ONE sentence.
    - Directly answer the user's question.
    - Use only the information available in the database result.
    - Preserve the exact numerical values and relevant names from the result.
    - For totals, averages, counts, percentages, or other numerical results, state the value clearly.
    - For highest or lowest results, clearly identify the corresponding item, region, product, category, or customer.
    - For comparisons, clearly state the comparison and relevant values when available.
    - If the result contains multiple rows, summarize only the information necessary to answer the question.
    - Do not show Python lists.
    - Do not show dictionaries.
    - Do not show Decimal().
    - Do not show SQL.
    - Do not mention the database.
    - Do not explain your reasoning.
    - Do not add information that is not present in the result.
    - Keep the answer concise and professional.
    - Return ONLY the final sentence.

    """

    response = llm.invoke(prompt)

    return {
        "analysis": response.content.strip()
    }

def decision_agent(state: AgentState):

    question = state["question"]
    analysis = state.get("analysis", "")
    policy_context = state.get("policy_context", "")

    prompt = f"""
    You are a Business Decision Support Agent.

    User Question:
    {question}

    Business Analysis:
    {analysis}

    Relevant Business Policy:
    {policy_context}

    Create the most appropriate business recommendation using ONLY
    the information provided above.

    Rules:
    - Return ONLY one sentence.
    - Maximum 25 words.
    - First state the important finding from the Business Analysis.
    - Then state the recommended action.
    - Connect the finding and recommendation naturally.
    - Use words such as "so", "therefore", or "you can" when appropriate.
    - Use ONLY information from the Business Analysis and Relevant Business Policy.
    - Do not mention SQL.
    - Do not mention RAG.
    - Do not mention the policy document.
    - Do not show reasoning.
    - Do not repeat the entire policy.
    - Do not invent information.

    General format:
    "[Finding], so [recommended action]."
    """

    response = llm.invoke(prompt)

    return {
        "recommendation": response.content.strip()
    }
# Now we need something that decides which agent should run.


def route_from_supervisor(state: AgentState):
    return state["route"]


def route_after_sql(state: AgentState):

    if state["route"] in ["SQL", "SQL_RAG"]:
        return "analytics"

    return "final"


def route_after_analytics(state: AgentState):

    if state["route"] == "SQL_RAG":
        return "rag"

    return "final"

def route_after_rag(state: AgentState):

    if state["route"] == "SQL_RAG":
        return "decision"

    return "policy_answer"

def final_answer(state: AgentState):

    if state.get("recommendation"):
        return {
            "final_answer": state["recommendation"]
        }

    if state.get("analysis"):
        return {
            "final_answer": state["analysis"]
        }

    if state.get("sql_result"):
        return {
            "final_answer": state["sql_result"]
        }

    return {
        "final_answer": "I could not find enough information to answer the question."
    }
    
#Now LangGraph needs to know where to send the state.
#def route_agent(state:AgentState):
     #return state["next_agent"]

# Create Langgraph    
graph = StateGraph(AgentState)

graph.add_node("supervisor", supervisor)
graph.add_node("sql", sql_agent)
graph.add_node("analytics", analytics_agent)
graph.add_node("rag", rag_agent)
graph.add_node("policy_answer", policy_answer_agent)
graph.add_node("decision", decision_agent)
graph.add_node("final_answer", final_answer)


# START → Supervisor
graph.add_edge(START, "supervisor")


# Supervisor decides the route
graph.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "SQL": "sql",
        "RAG": "rag",
        "SQL_RAG": "sql"
    }
)


# SQL → Analytics or Final
graph.add_conditional_edges(
    "sql",
    route_after_sql,
    {
        "analytics": "analytics",
        "final": "final_answer"
    }
)


# Analytics → RAG or Final
graph.add_conditional_edges(
    "analytics",
    route_after_analytics,
    {
        "rag": "rag",
        "final": "final_answer"
    }
)


# RAG → Decision
graph.add_conditional_edges(
    "rag",
    route_after_rag,
    {
        "decision": "decision",
        "policy_answer": "policy_answer"
    }
)

graph.add_edge("policy_answer","final_answer")

# Decision → Final
graph.add_edge("decision", "final_answer")


# Final → END
graph.add_edge("final_answer", END)

agent = graph.compile()

#But there is a problem- suppose "Which region had the lowest
#  sales and what should we do about it? The supervisor might
# only choose sql. Here we need workflow where agents can work
# together. Thats were langgraph conditional routing works."

# We dont want to see raw outputs from the above agents.


question = "Can we offer a 20% discount to the lowest-performing region?"

result = agent.invoke({
    "question": question
})

print(result["final_answer"])