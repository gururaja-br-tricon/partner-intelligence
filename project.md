1. Problem Statement
Business problem

[Likely] The demo is modeled around a partner ecosystem where a company such as TCC has information about partner organizations coming from different sources.

The goal is to let a user ask natural-language questions about partners without needing to know:

which database contains the information
which table contains it
which PDF contains it
how the information is related
what query needs to be executed

For example, a user should be able to ask:

"Find Microsoft Gold partners in Texas with Expert AI capabilities."

or:

"Which partners have strong cybersecurity capabilities?"

or:

"Tell me more about Nexora's AI capabilities."

or a multi-turn question:

"Find Microsoft partners in Texas with AI expertise."

Then:

"Which of them are MSPs?"

Then:

"Tell me more about the strongest one."

[Certain] The LLM should determine which MCP tool or tools are needed to answer these questions.

2. Scope of Partner Intelligence

[Certain] We defined the primary information domain as:

Partner Profile & Capability

This consists of four major dimensions.

Partner Profile & Capability
│
├── Company Attributes
│   ├── Partner name
│   ├── Location
│   ├── Country
│   ├── State
│   ├── City
│   ├── Industry
│   ├── Employee count
│   ├── Revenue
│   ├── Founded year
│   └── Status
│
├── Capabilities
│   ├── AI
│   ├── Cybersecurity
│   ├── Cloud
│   ├── DevOps
│   ├── Application Modernization
│   ├── Proficiency level
│   ├── Years of experience
│   └── Certification count
│
├── Partner Program Participation
│   ├── Vendor
│   ├── Program
│   ├── Partner tier
│   ├── Status
│   └── Enrollment date
│
└── Partner Classification
    ├── MSP
    ├── System Integrator
    ├── Consulting
    ├── Technology Partner
    └── etc.
3. Why we have two data sources

[Certain] We deliberately separated the data into structured and unstructured information.

Structured data → Snowflake

The CSVs contain information that is naturally represented as rows and columns:

Partner
Capability
Program
Classification

This is now in:

PARTNER_INTELLIGENCE_DB
        │
        └── PARTNER_DATA
              │
              ├── PARTNER_MASTER
              ├── PARTNER_CAPABILITIES
              ├── PARTNER_PROGRAMS
              └── PARTNER_CLASSIFICATIONS
Unstructured data → RAG

The PDFs contain richer descriptive information about each partner.

For example:

Partner overview
Service descriptions
Technology expertise
Industry experience
Differentiators
Case studies
Delivery capabilities
Business descriptions

These are much better suited to document retrieval than SQL.

4. High-Level Architecture

[Certain] The architecture we're building is:

                         ┌───────────────────────┐
                         │         User          │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │      LLM / Agent      │
                         │                       │
                         │ Understands question   │
                         │ Maintains context     │
                         │ Chooses MCP tool(s)   │
                         └───────────┬───────────┘
                                     │
                         ┌───────────┴───────────┐
                         │                       │
                         ▼                       ▼
               ┌─────────────────┐    ┌─────────────────┐
               │ Structured MCP  │    │ Document MCP    │
               │ Tools           │    │ Tools           │
               └────────┬────────┘    └────────┬────────┘
                        │                      │
                        ▼                      ▼
                 ┌─────────────┐        ┌─────────────┐
                 │  Snowflake  │        │     RAG     │
                 │             │        │             │
                 │ Partner     │        │ PDF         │
                 │ Data        │        │ Documents   │
                 └─────────────┘        └─────────────┘

The important part is this:

                    LLM
                     │
              decides what to use
                     │
             ┌───────┴───────┐
             ▼               ▼
        Snowflake           RAG
        structured        unstructured
           data               data
5. HLD: Components

[Certain] The codebase is currently organized roughly like this:

partner-intelligence/
│
├── app/
│   │
│   ├── mcp/
│   │   ├── server.py
│   │   └── test_mcp.py
│   │
│   └── repository/
│       ├── partner_repository.py
│       ├── test_partner_repository.py
│       ├── snowflake_partner_repository.py
│       └── test_snowflake_repository.py
│
├── data/
│   │
│   ├── generator/
│   │   ├── main.py
│   │   ├── partner_master_generator.py
│   │   ├── capability_generator.py
│   │   ├── program_generator.py
│   │   ├── classification_generator.py
│   │   ├── document_generator.py
│   │   └── validation.py
│   │
│   └── generated/
│       ├── partner_master.csv
│       ├── partner_capabilities.csv
│       ├── partner_programs.csv
│       ├── partner_classifications.csv
│       │
│       └── documents/
│           ├── P001.pdf
│           ├── P002.pdf
│           ├── ...
│           └── P010.pdf
│
├── .env
└── ...

[Certain] We intentionally generated the data first instead of starting with the agent.

That gave us a controlled dataset against which we can test every layer.

6. Data Generation Layer

[Certain] This part is complete.

We created 10 predefined partners rather than randomly generating company names.

The generator produced:

10 partners
44 capability records
25 program records
20 classification records
10 PDFs

The generated CSVs are:

partner_master.csv
partner_capabilities.csv
partner_programs.csv
partner_classifications.csv

And PDFs:

P001.pdf
P002.pdf
...
P010.pdf
7. Validation Layer

[Certain] We also created validation before connecting the data to Snowflake.

The validation confirmed:

Partner IDs                 OK
Partner names               OK
Required columns            OK

Capability foreign keys     OK
Capability relationships    OK
Proficiency levels          OK

Program foreign keys        OK
Program relationships       OK
Enrollment dates            OK

Classification foreign keys OK
Classification relationships OK
Primary classifications    OK

PDF documents               OK

Every partner has:
    capabilities            OK
    programs                OK
    classifications         OK

We also validated demo scenarios such as:

Texas + Microsoft Gold + AI
AWS + Cybersecurity
Microsoft + Advanced/Expert AI
MSP + Cybersecurity

So the dataset is intentionally designed to support the questions we're going to ask.

8. Repository Layer

The purpose was to establish the data access contract independently from the storage technology.

Conceptually:

MCP
 │
 ▼
PartnerRepository
 │
 ▼
CSV

We tested operations such as:

get_partner()
get_capabilities()
get_programs()
get_classifications()
search_partners()

This worked.

9. Snowflake Layer

Snowflake environment now contains:

PARTNER_INTELLIGENCE_DB
│
└── PARTNER_DATA
    │
    ├── PARTNER_MASTER
    ├── PARTNER_CAPABILITIES
    ├── PARTNER_PROGRAMS
    └── PARTNER_CLASSIFICATIONS

We loaded:

10 partner records
44 capability records
25 program records
20 classification records

All counts were verified.

10. Snowflake Repository

app/repository/snowflake_partner_repository.py

It currently supports:

get_partner()
get_capabilities()
get_programs()
get_classifications()
get_partner_profile()
search_partners()

We tested the repository independently.

For example:

Texas
+
Microsoft
+
Gold
+
Expert AI
+
MSP

returned:

P001
Nexora Technologies

So:

Python
   ↓
Snowflake connector
   ↓
Snowflake
   ↓
Correct result

is proven.

11. MCP Layer


Your MCP server is using:

from mcp.server import MCPServer

because you're on MCP version 2.0.0.

We verified that the server imports successfully.

We also verified the registered tool:

search_partners

and its generated input schema.

The tool exposes filters such as:

headquarters_state
headquarters_country
industry
status
capability
proficiency_level
vendor
program_name
partner_tier
classification

That is important because the LLM can now decide which parameters to provide.

12. Current MCP Flow

[Certain] Your current working flow is:

LLM
 │
 │ decides:
 │ "I need partners in Texas
 │  with Expert AI,
 │  Microsoft Gold,
 │  MSP"
 │
 ▼
search_partners(
    headquarters_state="Texas",
    capability="AI",
    proficiency_level="Expert",
    vendor="Microsoft",
    partner_tier="Gold",
    classification="MSP"
)
 │
 ▼
SnowflakePartnerRepository
 │
 ▼
Snowflake
 │
 ▼
P001

This is the core structured-data capability.

13. Where We Are Right Now

[Certain] I would mark the project status like this:

Component	Status
Problem/use-case definition	✅ Done
Partner question domain	✅ Done
Dummy data design	✅ Done
Partner CSV generation	✅ Done
PDF generation	✅ Done
Dataset validation	✅ Done
Local CSV repository	✅ Done
Snowflake account	✅ Done
Snowflake database	✅ Done
Snowflake schema	✅ Done
Snowflake tables	✅ Done
CSV → Snowflake	✅ Done
Snowflake connection from Python	✅ Done
Snowflake repository	✅ Done
search_partners() against Snowflake	✅ Done
MCP server	✅ Done
MCP → Snowflake	✅ Done
MCP search testing	✅ Done
PDF → RAG	⏳ Next
RAG retrieval MCP tool	⏳ Next
Multi-step agent	⏳ Teammate
Multi-turn conversation	⏳ Teammate
Final LLM integration	⏳ Teammate
End-to-end demo	⏳ Final
14. What You Own vs What Your Teammate Owns

[Certain] This division is actually quite clean.

Your responsibility
                    YOUR WORK
                       │
        ┌──────────────┴──────────────┐
        │                             │
   Data Layer                    Tool Layer
        │                             │
        ▼                             ▼
 Dummy data                     MCP server
        │                             │
        ▼                             ▼
 Snowflake                      Snowflake tool
        │
        ▼
 PDF documents
        │
        ▼
 RAG
        │
        ▼
 RAG MCP tool
Your teammate
                 TEAMMATE
                     │
                     ▼
                  LLM Agent
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Planning    Tool       Memory/
                  selection   Context
                     │
                     ▼
                 Final answer

[Likely] The interface between your work and your teammate's work should therefore be MCP.

Your teammate should not need to know:

Snowflake SQL
CSV structure
PDF chunking
Embedding model
Vector database

They should only need to know:

What MCP tools exist?
What are their descriptions?
What arguments do they accept?
What do they return?

That's the clean separation.

15. The Remaining Architecture

[Certain] After we finish RAG, the final system should look like this:

                              USER
                                │
                                ▼
                         ┌─────────────┐
                         │ LLM / Agent │
                         └──────┬──────┘
                                │
                    decides which tool(s)
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
        ┌─────────────────┐           ┌─────────────────┐
        │ Partner Search  │           │ Partner         │
        │ MCP Tool        │           │ Knowledge MCP   │
        └────────┬────────┘           └────────┬────────┘
                 │                             │
                 ▼                             ▼
        ┌─────────────────┐           ┌─────────────────┐
        │ Snowflake       │           │ RAG Pipeline    │
        │ Repository      │           │                 │
        └────────┬────────┘           └────────┬────────┘
                 │                             │
                 ▼                             ▼
        ┌─────────────────┐           ┌─────────────────┐
        │ Structured      │           │ Vector Store    │
        │ Partner Data    │           │ + PDF chunks    │
        └─────────────────┘           └─────────────────┘

And the really useful part is when the agent combines them:

User:
"Which Microsoft Gold partners in Texas
are strong in AI, and why would you recommend them?"

                  │
                  ▼
                 LLM
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
 search_partners       retrieve_partner_info
        │                   │
        ▼                   ▼
   Snowflake               RAG
        │                   │
        └─────────┬─────────┘
                  ▼
              LLM synthesis
                  │
                  ▼
            Final answer