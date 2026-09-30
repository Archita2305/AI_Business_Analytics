from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()
llm= ChatGroq(model='openai/gpt-oss-120b',temperature=0)
schema= """ Table name: sales

Columns:
- order_id: INTEGER
- order_date: DATE
- product: VARCHAR
- category: VARCHAR
- region: VARCHAR
- quantity: INTEGER
- sales: DECIMAL
- profit: DECIMAL
- customer: VARCHAR"""

question= "What were our total sales"
prompt=  f"""Act like you are a PostgreSQL expert. Only use the
database schema provided below.
DATABASE SCHEMA:{schema}
BUSINESS QUESTION:{question}.
Generate a SQL querry for the business question asked. Only 
give answer from the schema and answer should be SQL querry
only. Dont give any other information."""

response= llm.invoke(prompt)
print(response.content)