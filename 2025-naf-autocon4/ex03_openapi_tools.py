"""
Auto-generate Tools from OpenAPI Specifications

This example parses an OpenAPI spec and automatically converts operations to
Anthropic tool definitions with appropriate schemas, descriptions, and parameter validation.
"""

import yaml
from typing import Any


NHL_OPENAPI_SPEC = """
openapi: 3.0.0
info:
  title: NHL Stats API
  version: 1.0.0
  description: Public API for NHL player statistics
servers:
  - url: https://api-web.nhle.com/v1
    description: Main stats API
  - url: https://search.d3.nhle.com/api/v1
    description: Search API
paths:
  /search/player:
    get:
      operationId: searchPlayer
      summary: Search for NHL players by name
      description: Searches the NHL player database and returns matching players with their IDs
      parameters:
        - name: q
          in: query
          required: true
          description: Player name to search for (e.g., "Connor McDavid")
          schema:
            type: string
      responses:
        '200':
          description: List of matching players
  /player/{playerId}/landing:
    get:
      operationId: getPlayerStats
      summary: Get comprehensive stats for a specific player
      description: Returns detailed statistics including goals, assists, points, special teams, and more
      parameters:
        - name: playerId
          in: path
          required: true
          description: Numeric player ID (e.g., 8478402 for Connor McDavid)
          schema:
            type: integer
      responses:
        '200':
          description: Player statistics and biographical information
"""


def openapi_to_tools(spec_yaml: str) -> list[dict[str, Any]]:
    """
    Convert OpenAPI specification to Anthropic tool definitions.

    Parses an OpenAPI YAML spec and generates tool definitions compatible with
    Anthropic's function calling API. This demonstrates how frameworks can
    automatically scale to many endpoints without manual tool definitions.

    Args:
        spec_yaml: OpenAPI specification in YAML format

    Returns:
        List of tool definitions in Anthropic format
    """
    try:
        spec = yaml.safe_load(spec_yaml)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML specification: {e}")

    tools = []

    # extract paths and operations from OpenAPI spec
    paths = spec.get("paths", {})

    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method not in ["get", "post", "put", "delete", "patch"]:
                continue

            # build tool definition from operation
            tool = {
                "name": operation.get("operationId", f"{method}_{path.replace('/', '_')}"),
                "description": operation.get("description", operation.get("summary", "")),
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }

            # process parameters (query, path, header, cookie)
            parameters = operation.get("parameters", [])
            for param in parameters:
                param_name = param["name"]
                param_schema = param.get("schema", {"type": "string"})

                # Add parameter to input schema
                tool["input_schema"]["properties"][param_name] = {
                    "type": param_schema.get("type", "string"),
                    "description": param.get("description", "")
                }

                # add to required list if parameter is required
                if param.get("required", False):
                    tool["input_schema"]["required"].append(param_name)

            tools.append(tool)

    return tools

if __name__ == "__main__":

    # demonstrate OpenAPI to tools conversion
    print("\nNHL Stats API - OpenAPI Tool Generation Demo")
    print("=" * 50)
    print()

    # generate tools from specification
    tools = openapi_to_tools(NHL_OPENAPI_SPEC)

    print(f"Generated {len(tools)} tools from OpenAPI spec:\n")

    # display each generated tool
    for tool in tools:
        print(f"Tool: {tool['name']}")
        print(f"Description: {tool['description']}")
        print(f"Parameters:")

        properties = tool['input_schema']['properties']
        required = tool['input_schema'].get('required', [])

        if not properties:
            print("  (none)")
        else:
            for param_name, param_info in properties.items():
                required_marker = " (required)" if param_name in required else ""
                print(f"  - {param_name}: {param_info['type']}{required_marker}")
                if param_info.get('description'):
                    print(f"    {param_info['description']}")

        print()

    print("\nBenefit: OpenAPI specs auto-generate tool definitions")
    print("vs. ex02 which requires manual schema creation for each endpoint")
    print("\nThese tools can be passed directly to the Anthropic API:")
    print("  client.messages.create(model='...', tools=tools, ...)")