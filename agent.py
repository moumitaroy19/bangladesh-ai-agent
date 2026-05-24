"""
Multi-Tool AI Agent for Bangladesh
====================================
Assignment: Module 23 – Exam Week 4

This agent routes queries to:
  - InstitutionsDBTool  → institutions.db
  - HospitalsDBTool     → hospitals.db
  - RestaurantsDBTool   → restaurants.db
  - WebSearchTool       → Tavily / general knowledge
"""

import os
import sqlite3
from typing import Optional

# ── LangChain ──────────────────────────────────────────────────────────────
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import BaseTool
from langchain_anthropic import ChatAnthropic          # or ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import hub

# ── ENV ────────────────────────────────────────────────────────────────────
# Set these in your environment or .env file:
#   ANTHROPIC_API_KEY   = "sk-ant-..."   (used here; swap for OPENAI_API_KEY if preferred)
#   TAVILY_API_KEY      = "tvly-..."
# For Colab: use userdata.get() – see setup_colab.py

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
TAVILY_API_KEY    = os.getenv("TAVILY_API_KEY", "")


# ══════════════════════════════════════════════════════════════════════════════
# 1.  DB QUERY HELPER
# ══════════════════════════════════════════════════════════════════════════════

def query_db(db_path: str, sql: str) -> str:
    """Run a SQL query and return a human-readable string of results."""
    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        con.close()

        if not rows:
            return "No results found."

        # Build a simple markdown-style table
        lines = [" | ".join(cols)]
        lines.append("-" * len(lines[0]))
        for row in rows[:20]:            # cap at 20 rows for readability
            lines.append(" | ".join(str(v) for v in row))

        if len(rows) > 20:
            lines.append(f"... ({len(rows)} total rows, showing first 20)")

        return "\n".join(lines)

    except Exception as exc:
        return f"SQL error: {exc}"


# ══════════════════════════════════════════════════════════════════════════════
# 2.  LANGCHAIN TOOLS
# ══════════════════════════════════════════════════════════════════════════════

class InstitutionsDBTool(BaseTool):
    name: str = "InstitutionsDBTool"
    description: str = (
        "Use this tool to answer questions about Bangladeshi educational and "
        "government institutions (universities, colleges, schools, ministries, etc.). "
        "Input must be a valid SQLite SELECT query against the 'institutions' table. "
        "Columns: id, name, type, district, division, address, founded_year, "
        "contact, website."
    )

    def _run(self, sql: str) -> str:
        return query_db("institutions.db", sql)

    async def _arun(self, sql: str) -> str:
        return self._run(sql)


class HospitalsDBTool(BaseTool):
    name: str = "HospitalsDBTool"
    description: str = (
        "Use this tool to answer questions about Bangladeshi hospitals, clinics, "
        "and healthcare facilities (beds, doctors, location, type, etc.). "
        "Input must be a valid SQLite SELECT query against the 'hospitals' table. "
        "Columns: id, name, type, district, division, address, beds, doctors, "
        "contact, established_year."
    )

    def _run(self, sql: str) -> str:
        return query_db("hospitals.db", sql)

    async def _arun(self, sql: str) -> str:
        return self._run(sql)


class RestaurantsDBTool(BaseTool):
    name: str = "RestaurantsDBTool"
    description: str = (
        "Use this tool to answer questions about Bangladeshi restaurants, "
        "food types, cuisine, ratings, and locations. "
        "Input must be a valid SQLite SELECT query against the 'restaurants' table. "
        "Columns: id, name, cuisine, district, division, address, rating, "
        "price_range, contact."
    )

    def _run(self, sql: str) -> str:
        return query_db("restaurants.db", sql)

    async def _arun(self, sql: str) -> str:
        return self._run(sql)


# ══════════════════════════════════════════════════════════════════════════════
# 3.  AGENT FACTORY
# ══════════════════════════════════════════════════════════════════════════════

def build_agent() -> AgentExecutor:
    # LLM (Claude Sonnet via Anthropic – swap to ChatOpenAI if you prefer)
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        temperature=0,
        anthropic_api_key=ANTHROPIC_API_KEY,
    )

    # Tools
    web_search = TavilySearchResults(
        max_results=5,
        tavily_api_key=TAVILY_API_KEY,
    )
    web_search.name = "WebSearchTool"
    web_search.description = (
        "Use this tool for general knowledge questions: policies, definitions, "
        "cultural context, government agencies, current events about Bangladesh. "
        "Input: a natural language search query."
    )

    tools = [
        InstitutionsDBTool(),
        HospitalsDBTool(),
        RestaurantsDBTool(),
        web_search,
    ]

    # ReAct prompt (pulled from LangChain Hub)
    prompt = hub.pull("hwchase17/react")

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,          # shows Thought → Action → Observation chain
        handle_parsing_errors=True,
        max_iterations=8,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 4.  MAIN
# ══════════════════════════════════════════════════════════════════════════════

EXAMPLE_QUERIES = [
    "How many hospitals are there in Dhaka district?",
    "List the top-rated restaurants in Chittagong.",
    "Which universities are located in Rajshahi division?",
    "What is the role of DGHS in Bangladesh?",
    "What is the total number of beds in all government hospitals?",
    "What is the national food policy of Bangladesh?",
]

if __name__ == "__main__":
    agent_executor = build_agent()

    print("\n" + "=" * 60)
    print("  🇧🇩  Bangladesh Multi-Tool AI Agent  🇧🇩")
    print("=" * 60)
    print("Type 'exit' to quit. Try one of these example queries:")
    for i, q in enumerate(EXAMPLE_QUERIES, 1):
        print(f"  {i}. {q}")
    print()

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break
        if not user_input:
            continue
        try:
            result = agent_executor.invoke({"input": user_input})
            print(f"\n🤖 Agent: {result['output']}\n")
        except Exception as e:
            print(f"Error: {e}\n")
