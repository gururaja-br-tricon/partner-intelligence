# Partner Intelligence

Partner Intelligence is a demo multi-step, multi-turn agent system that enables an LLM to discover and retrieve partner information from multiple data sources through MCP (Model Context Protocol).

The project currently focuses on structured partner data stored in Snowflake and exposes partner-search capabilities through an MCP server.

The next phase will add PDF-based RAG retrieval and expose that capability through MCP as well.

---

## Architecture

```text
                         User
                           |
                           v
                          LLM
                           |
                           v
                      MCP Client
                           |
                           v
                 Partner Intelligence
                    MCP Server
                    /          \
                   /            \
                  v              v
             Snowflake          RAG
            Structured        PDF Data
               Data
```

The LLM is responsible for deciding which MCP tool to use.

The MCP server is responsible for exposing tools and executing them.

---

## Current Data Sources

### Structured Data

Partner structured data is stored in Snowflake.

The current dataset contains:

* Partner master information
* Partner capabilities
* Partner program participation
* Partner classifications

### Documents

Partner-specific PDF documents are generated locally.

```text
data/generated/documents/
├── P001.pdf
├── P002.pdf
├── ...
└── P010.pdf
```

These documents will be used for the RAG component.

Generated CSV and PDF files are intentionally excluded from Git using `.gitignore`.

---

## Partner Data Model

### Partner Master

Contains company-level attributes:

* Partner ID
* Partner name
* Status
* Website
* Founded year
* Employee count
* Annual revenue
* Industry
* Headquarters country
* Headquarters state
* Headquarters city

### Partner Capabilities

Contains:

* Capability
* Proficiency level
* Years of experience
* Certification count

### Partner Programs

Contains:

* Vendor
* Program name
* Partner tier
* Status
* Enrollment date

### Partner Classifications

Contains:

* Classification
* Primary classification

---

## Project Structure

```text
partner-intelligence/
│
├── app/
│   ├── mcp/
│   │   ├── server.py
│   │   ├── http_server.py
│   │   └── test_mcp_client.py
│   │
│   └── repository/
│       ├── partner_repository.py
│       ├── test_partner_repository.py
│       ├── snowflake_partner_repository.py
│       └── test_snowflake_repository.py
│
├── data/
│   ├── generator/
│   │   ├── main.py
│   │   ├── document_generator.py
│   │   └── validation.py
│   │
│   └── generated/
│       ├── partner_master.csv
│       ├── partner_capabilities.csv
│       ├── partner_programs.csv
│       ├── partner_classifications.csv
│       └── documents/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## MCP Server

The MCP server currently exposes the following tool:

```text
search_partners
```

The tool supports searching using:

* Headquarters state
* Headquarters country
* Industry
* Status
* Capability
* Proficiency level
* Vendor
* Program name
* Partner tier
* Classification

The MCP server retrieves structured data from Snowflake through the repository layer.

---

## MCP Architecture

```text
MCP Client
     |
     | Streamable HTTP
     v
MCP Server
     |
     v
search_partners()
     |
     v
SnowflakePartnerRepository
     |
     v
Snowflake
```

The repository layer is responsible for data access.

The MCP layer is responsible for exposing that functionality as an MCP tool.

---

## Running the MCP Server

Start the Streamable HTTP server from the project root:

```powershell
python app/mcp/http_server.py
```

The server runs on:

```text
http://127.0.0.1:8000
```

The MCP endpoint is:

```text
http://127.0.0.1:8000/mcp
```

---

## Testing MCP Connectivity

Keep the MCP server running in one terminal.

Then, from another terminal:

```powershell
python app/mcp/test_mcp_client.py
```

The test client:

1. Connects to the MCP server.
2. Initializes an MCP session.
3. Discovers available tools.
4. Calls `search_partners`.
5. Prints the returned Snowflake data.

---

## Example Query

A query such as:

```text
Find Texas-based Microsoft Gold partners with Expert AI capability.
```

can be translated by the LLM into an MCP tool call similar to:

```text
search_partners(
    headquarters_state="Texas",
    capability="AI",
    proficiency_level="Expert",
    vendor="Microsoft",
    partner_tier="Gold"
)
```

The MCP server passes the request to the Snowflake repository, which retrieves the matching partner records.

---

## Demo Dataset

The demo currently contains 10 predefined partner organizations.

The dataset was intentionally designed to support questions around:

### Partner Profile & Capability

* Company attributes
* Capabilities
* Partner program participation
* Partner classification

It also supports multi-condition partner discovery such as:

```text
Texas + Microsoft Gold + Expert AI
```

and:

```text
Texas + Microsoft Gold + AI + MSP
```

---

## Validation

The dataset generation process includes validation for:

* Required columns
* Partner IDs
* Foreign-key relationships
* Capability relationships
* Program relationships
* Classification relationships
* Enrollment dates
* PDF document generation
* Business relationship coverage
* Demo scenarios

The generated dataset must pass validation before being used.

---

## Snowflake

The current Snowflake setup uses:

```text
Database:
PARTNER_INTELLIGENCE_DB

Schema:
PARTNER_DATA
```

Tables:

```text
PARTNER_MASTER
PARTNER_CAPABILITIES
PARTNER_PROGRAMS
PARTNER_CLASSIFICATIONS
```

Snowflake credentials should be stored in environment variables and must not be committed to Git.

Example `.env` configuration:

```text
SNOWFLAKE_ACCOUNT=<account>
SNOWFLAKE_USER=<user>
SNOWFLAKE_PASSWORD=<password>
SNOWFLAKE_DATABASE=PARTNER_INTELLIGENCE_DB
SNOWFLAKE_SCHEMA=PARTNER_DATA
SNOWFLAKE_WAREHOUSE=<warehouse>
```

Do not commit `.env`.

---

## RAG - Planned

The next phase will add PDF-based retrieval.

The planned flow is:

```text
Partner PDFs
     |
     v
PDF Text Extraction
     |
     v
Chunking
     |
     v
Embeddings
     |
     v
Vector Store
     |
     v
Retriever
     |
     v
MCP Tool
```

The final MCP server will expose both structured and document-based retrieval capabilities.

```text
                    MCP Server
                    /         \
                   /           \
                  v             v
        search_partners()   search_partner_documents()
                  |             |
                  v             v
              Snowflake         RAG
```

---

## Agent Use Case

The final system is intended to support multi-step and multi-turn questions.

For example:

```text
Find Microsoft Gold partners in Texas with Expert AI capability
and explain their strengths.
```

The LLM may:

```text
1. Call search_partners()
2. Identify matching partners
3. Call the document/RAG tool
4. Retrieve additional information from partner PDFs
5. Combine the results
6. Generate the final response
```

Tool selection is performed by the LLM/agent rather than hard-coded application logic.

---

## Current Status

### Completed

* Demo partner dataset generation
* Predefined partner organizations
* Partner master CSV
* Partner capabilities CSV
* Partner programs CSV
* Partner classifications CSV
* Partner PDF generation
* Dataset validation
* Snowflake database setup
* Snowflake tables
* Snowflake data validation
* Partner repository
* Snowflake repository
* MCP server
* `search_partners` MCP tool
* Local MCP tool testing
* Streamable HTTP MCP server
* MCP client connectivity testing

### In Progress / Next

* PDF RAG pipeline
* PDF retrieval MCP tool
* End-to-end MCP + RAG testing
* LLM integration
* Multi-step agent testing

---

## Important

This project is a demonstration/prototype.

The partner organizations and associated data are synthetic and created specifically for demonstration and testing purposes.
