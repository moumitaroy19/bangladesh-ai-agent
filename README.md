# 🇧🇩 Multi-Tool AI Agent for Bangladesh
### Module 23 · Exam Week-4

An AI agent that routes user queries intelligently across **three SQLite databases** (institutions, hospitals, restaurants) and a **web search tool** using LangChain's ReAct framework.

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────┐
│   LangChain ReAct Agent (LLM)   │
│   claude-sonnet / gpt-4o-mini   │
└────────────┬────────────────────┘
             │  routes to
    ┌─────────┼──────────────────────┐
    │         │                      │
    ▼         ▼                      ▼
InstitutionsDB  HospitalsDB    RestaurantsDB   WebSearchTool
 (institutions   (hospitals       (restaurants    (Tavily API)
     .db)           .db)              .db)
```

### Tool Routing Logic
| Query Type | Tool Used |
|---|---|
| "How many hospitals in Dhaka?" | HospitalsDBTool |
| "Top restaurants in Chittagong?" | RestaurantsDBTool |
| "Universities in Rajshahi?" | InstitutionsDBTool |
| "What is DGHS?" / policy questions | WebSearchTool |

---

## 📁 Project Structure

```
bangladesh_agent/
├── agent.py              # Main agent + all LangChain tools
├── setup_databases.py    # Downloads HuggingFace datasets → SQLite DBs
├── colab_demo.py         # Google Colab cell-by-cell demo
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/bangladesh-ai-agent.git
cd bangladesh-ai-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set API keys
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export TAVILY_API_KEY="tvly-..."
```
> Get Tavily key free at https://tavily.com  
> Get Anthropic key at https://console.anthropic.com

### 4. Build the databases (run ONCE)
```bash
python setup_databases.py
```
This downloads three HuggingFace datasets and creates:
- `institutions.db` → table `institutions`
- `hospitals.db`    → table `hospitals`
- `restaurants.db`  → table `restaurants`

### 5. Run the agent
```bash
python agent.py
```

---

## 🧪 Example Queries

```
You: How many hospitals are there in Dhaka district?
You: List the top-rated restaurants in Chittagong.
You: Which universities are located in Rajshahi division?
You: What is the role of DGHS in Bangladesh?
You: What is the total number of hospital beds across Bangladesh?
You: What is the national food policy of Bangladesh?
```

---

## 📓 Google Colab

Open `colab_demo.py` — each section maps to one Colab cell.  
Store your API keys in **Colab Secrets** (🔑 icon in sidebar).

---

## 🗄️ Datasets Used

| Dataset | HuggingFace Link |
|---|---|
| Institutional Information of Bangladesh | [Mahadih534/Institutional-Information-of-Bangladesh](https://huggingface.co/datasets/Mahadih534/Institutional-Information-of-Bangladesh) |
| All Bangladeshi Hospitals | [Mahadih534/all-bangladeshi-hospitals](https://huggingface.co/datasets/Mahadih534/all-bangladeshi-hospitals) |
| Bangladeshi Restaurant Data | [Mahadih534/Bangladeshi-Restaurant-Data](https://huggingface.co/datasets/Mahadih534/Bangladeshi-Restaurant-Data) |

---

## 🧠 Tech Stack

- **LangChain** – Agent framework & tool orchestration
- **Claude Sonnet** (Anthropic) – LLM backbone
- **Tavily** – Web search API
- **SQLite** – Local database engine
- **HuggingFace Datasets** – Data source
- **Pandas** – Data cleaning

---
