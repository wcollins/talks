# Is MCP just an _API Abstraction_?
This repository contains the _slides_ and code examples used in my [AutoCon4](https://networkautomation.forum/autocon4#program) talk.

## Overview of Examples
I am an automation fan. I am also a hockey fan. There is a public and free to use _API_ for gathering various types of data. What better way to demonstrate the differences of using an API directly, versus instantiating and using an MCP server? 

### Basic API example - `ex01_basic_api.py`
Traditional HTTP requests to NHL API using the `requests` library, requiring hardcoded player IDs to fetch statistics.

### LLM Function Calling with RESTful APIs - `ex02_function_calling.py`
Manual Claude function calling with hand-written tool schemas, demonstrating the "glue code" pattern needed to connect LLMs to REST APIs.

### Auto Generate Tools from OpenAPI Spec - `ex03_openapi_tools.py`
Auto-generates Anthropic tool definitions from OpenAPI YAML specifications, eliminating manual schema creation required in ex02.

### FastMCP Server Exposing Tools via Decorators - `ex04_mcp_server.py`
MCP server using FastMCP framework with simple `@mcp.tool()` decorators, providing natural language access to NHL stats through Claude Desktop.


## Prerequisites

- Python 3.10 or higher
- [UV](https://docs.astral.sh/uv/) package manager
- [Claude Desktop](https://claude.ai/download) (for MCP example)

## Quick Start

### 1. Set up the environment

```bash
# Clone repo
git clone https://github.com/wcollins/talks.git
cd talks/2025-naf-autocon4

# Create venv
uv venv --python 3.11

# Activate venv
source .venv/bin/activate

# Install dependencies
uv sync
```

## Running the Examples

### API Example

The traditional approach - direct API calls requiring player IDs:

```bash
python ex01_basic_api.py
```

**What it does:**
- Fetches stats for Connor McDavid _(player ID: 8478402)_
- Makes a direct HTTP GET request the NHL API
- Parses JSON response manually
- Displays formatted statistics

### LLM Function Calling Example

Demonstrates Claude API function calling with manual tool definitions:

```bash
# Set your API key
export ANTHROPIC_API_KEY='your-key-here'

# Run the example
python ex02_function_calling.py
```

**What it does:**
- Defines tools manually using JSON schema format
- Implements custom agent loop between Claude and tool execution
- Converts player names to IDs automatically using `lookup_player_id()`
- Shows the "glue code" pattern required for each API endpoint

**Example queries in the code:**
- "What are Connor McDavid's stats this season?"
- "How many goals has Auston Matthews scored?"

**Key characteristics:**
- Requires hand-written tool schemas for each endpoint
- Custom message loop implementation (`run_agent()` function)
- Natural language input, structured tool calls output
- More flexible than direct API but requires significant setup code

### OpenAPI Tool Generation Example

Auto-generates tool definitions from OpenAPI specifications:

```bash
python ex03_openapi_tools.py
```

**What it does:**
- Parses embedded NHL API OpenAPI JSON/YAML specification
- Automatically generates Anthropic tool schemas from paths and operations
- Displays the generated tools with parameters and descriptions
- Demonstrates how frameworks can scale to many endpoints

**Benefit:**
Eliminates manual schema writing required in ex02. Instead of hand-crafting tool definitions, you provide an OpenAPI spec and tools are generated automatically.

### MCP Example

AI-native tool interface:

#### Step 1: Configure Claude Desktop

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

You can use the provided example config as a template:

```bash
# Get the absolute path to this directory
pwd

# Example output: /Users/william/talks/2025-naf-autocon4

# Copy and modify the example config
cat claude_desktop_config.example.json
```

Example configuration (replace `/absolute/path/to` with your actual path):
```json
{
  "mcpServers": {
    "nhl-stats": {
      "command": "/absolute/path/to/talks/2025-naf-autocon4/.venv/bin/python",
      "args": [
        "/absolute/path/to/talks/2025-naf-autocon4/ex04_mcp_server.py"
      ]
    }
  }
}
```

**Important:**
- Replace `/absolute/path/to` in BOTH places with your actual path (e.g., `/Users/yourname`)
- Use the output from `pwd` command
- Make sure you've created the virtual environment first (`uv venv` or `uv pip install requests anthropic mcp pyyaml`)

#### Step 3: Use in Claude Desktop

After restarting Claude Desktop, you can ask natural language questions:

**Example queries:**
- "What are Connor McDavid's stats this season?"
- "Get me the stats for Nathan MacKinnon"
- "How many points does Auston Matthews have?"
- "Who has more power play points, McDavid or Matthews?"
- "What's Leon Draisaitl's shooting percentage?"
- "Why do the Oilers stink so bad?"

**What makes this different:**
- No need to know player IDs - just use names
- AI understands context and can answer follow-up questions
- Tool is discoverable - Claude knows it exists and how to use it
- Automatic error handling and validation
- AI can interpret and compare stats intelligently

**Comprehensive stats returned:**
- **Player Info:** Name, team, position, games played
- **Scoring:** Goals, assists, points, shots, shooting %
- **Special Teams:** Power play and shorthanded goals/points
- **Impact:** Game-winning goals, overtime goals, plus/minus
- **Discipline:** Penalty minutes
