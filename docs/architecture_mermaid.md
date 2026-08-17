flowchart LR

%%==========================
%% Context Layer
%%==========================

subgraph CL["📚 Context Layer"]

A[User Query]

CB[Context Builder]

MEM[Conversation Memory]
RAG[RAG / Vector Store]
PROFILE[User Profile & Permissions]
RULES[Business Rules & Policies]
CACHE[Semantic Cache]

RANK[Context Ranking & Compression]

PROMPT[Prompt Construction]

A --> CB

CB --> MEM
CB --> RAG
CB --> PROFILE
CB --> RULES
CB --> CACHE

MEM --> RANK
RAG --> RANK
PROFILE --> RANK
RULES --> RANK
CACHE --> RANK

RANK --> PROMPT

end

%%==========================
%% LLM Orchestrator
%%==========================

subgraph ORCH["🧠 LLM Orchestrator"]

INTENT[Intent & Task Classification]

PLAN[Agent Planner / Workflow Engine]

GUARD[Guardrails<br/>PII • Safety • Compliance]

COORD[Multi-Agent Coordinator]

BI[BI Agent]
SALES[Sales Agent]
MARKETING[Marketing Agent]
SUPPORT[Support Agent]

TOOLS[MCP & Tool Orchestrator]

SNOW[Snowflake Tool]
SF[Salesforce Tool]
OMEDA[Omeda Tool]
REST[REST / Internal APIs]

ROUTER[LLM Router<br/>Cost • Latency • Quality]

CLAUDE[Anthropic]
OPENAI[OpenAI]
GEMINI[Gemini]
GROK[Grok]

VALIDATE[Response Validation]

RESP[Final Response]

PROMPT --> INTENT

INTENT --> PLAN
INTENT --> GUARD

PLAN --> COORD
GUARD --> COORD

COORD --> BI
COORD --> SALES
COORD --> MARKETING
COORD --> SUPPORT

BI --> TOOLS
SALES --> TOOLS
MARKETING --> TOOLS
SUPPORT --> TOOLS

TOOLS --> SNOW
TOOLS --> SF
TOOLS --> OMEDA
TOOLS --> REST

SNOW --> ROUTER
SF --> ROUTER
OMEDA --> ROUTER
REST --> ROUTER

ROUTER --> CLAUDE
ROUTER --> OPENAI
ROUTER --> GEMINI
ROUTER --> GROK

CLAUDE --> VALIDATE
OPENAI --> VALIDATE
GEMINI --> VALIDATE
GROK --> VALIDATE

VALIDATE --> RESP

end

%%==========================
%% Styling
%%==========================

classDef context fill:#E8F4FD,stroke:#1E88E5,stroke-width:2px,color:#000;
classDef orch fill:#FFF4E5,stroke:#FB8C00,stroke-width:2px,color:#000;
classDef llm fill:#F3E5F5,stroke:#8E24AA,stroke-width:2px,color:#000;
classDef tool fill:#E8F5E9,stroke:#43A047,stroke-width:2px,color:#000;
classDef output fill:#FCE4EC,stroke:#D81B60,stroke-width:2px,color:#000;

class A,CB,MEM,RAG,PROFILE,RULES,CACHE,RANK,PROMPT context;
class INTENT,PLAN,GUARD,COORD orch;
class ROUTER,CLAUDE,OPENAI,GEMINI,GROK llm;
class TOOLS,SNOW,SF,OMEDA,REST tool;
class VALIDATE,RESP output;