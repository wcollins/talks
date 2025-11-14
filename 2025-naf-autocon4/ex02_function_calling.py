"""
Function Calling Example with NHL Player Stats

This demonstrates how to use LLM function calling with REST APIs directly,
without MCP. This is the traditional approach that requires custom glue code
for each API integration.
"""

import anthropic
import requests
import json
from typing import Optional
from functools import lru_cache

# define tools (from API docs) - each API endpoint gets converted to a tool definition
tools = [
    {
        "name": "get_player_stats",
        "description": "Get current season statistics for an NHL player by name. Returns comprehensive stats including goals, assists, points, shooting percentage, special teams performance, and more.",
        "input_schema": {
            "type": "object",
            "properties": {
                "player_name": {
                    "type": "string",
                    "description": "Full or partial player name (e.g., 'Connor McDavid', 'McDavid')"
                }
            },
            "required": ["player_name"]
        }
    }
]

# api calls - "glue code" that connects the tool definition to the actual api
@lru_cache(maxsize=128)
def lookup_player_id(player_name: str) -> Optional[int]:
    """
    Convert player name to NHL player ID using search API.
    This is a common pattern: one API call to discover identifiers,
    then another to fetch the actual data.
    """
    url = "https://search.d3.nhle.com/api/v1/search/player"
    headers = {"User-Agent": "FunctionCallingDemo/1.0"}

    try:
        response = requests.get(
            url,
            params={"q": player_name},
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        data = response.json()

        if data and len(data) > 0:
            return data[0].get("playerId")
        return None
    except Exception as e:
        print(f"Error looking up player: {e}")
        return None


def get_player_stats(player_name: str) -> dict:
    """
    Fetch comprehensive NHL player statistics.
    Returns 17 stats across scoring, special teams, impact, and discipline.
    """

    # first, convert name to player ID
    player_id = lookup_player_id(player_name)
    if not player_id:
        raise ValueError(f"Player '{player_name}' not found")

    # then fetch the stats
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    headers = {"User-Agent": "FunctionCallingDemo/1.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # extract current season stats
        season_totals = data.get("featuredStats", {}).get("regularSeason", {}).get("subSeason", {})

        # return structured data
        return {
            "player_name": data.get("firstName", {}).get("default", "") + " " +
                          data.get("lastName", {}).get("default", ""),
            "team": season_totals.get("teamAbbrev", "N/A"),
            "position": data.get("position", "N/A"),
            "games_played": season_totals.get("gamesPlayed", 0),
            "goals": season_totals.get("goals", 0),
            "assists": season_totals.get("assists", 0),
            "points": season_totals.get("points", 0),
            "shots": season_totals.get("shots", 0),
            "shooting_pct": round(season_totals.get("shootingPctg", 0.0), 1),
            "power_play_goals": season_totals.get("powerPlayGoals", 0),
            "power_play_points": season_totals.get("powerPlayPoints", 0),
            "shorthanded_goals": season_totals.get("shorthandedGoals", 0),
            "shorthanded_points": season_totals.get("shorthandedPoints", 0),
            "game_winning_goals": season_totals.get("gameWinningGoals", 0),
            "ot_goals": season_totals.get("otGoals", 0),
            "plus_minus": season_totals.get("plusMinus", 0),
            "penalty_minutes": season_totals.get("pim", 0),
        }
    except Exception as e:
        raise ValueError(f"Error fetching stats for player ID {player_id}: {e}")


# agent loop; orchestrate conversation between LLM and tools
client = anthropic.Anthropic()

def run_agent(user_message: str) -> str:
    """
    Run an agentic conversation with function calling.

    The agent loop:
    1. Send user message to Claude with available tools
    2. If Claude wants to use a tool, execute it
    3. Send tool results back to Claude
    4. Repeat until Claude provides a final answer
    """
    messages = [{"role": "user", "content": user_message}]

    while True:

        # call claude with tools available
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )

        # check if claude wants to use a tool
        if response.stop_reason == "tool_use":
            # Extract the tool use request
            tool_use = next(block for block in response.content if block.type == "tool_use")

            print(f"[Agent] Using tool: {tool_use.name}")
            print(f"[Agent] Parameters: {tool_use.input}")

            # execute the appropriate function
            try:
                if tool_use.name == "get_player_stats":
                    result = get_player_stats(**tool_use.input)
                    result_content = json.dumps(result, indent=2)
                    is_error = False
                else:
                    result_content = f"Unknown tool: {tool_use.name}"
                    is_error = True
            except Exception as e:
                result_content = f"Error: {str(e)}"
                is_error = True

            print(f"[Agent] Tool result: {result_content[:100]}...")

            # add assistant's response and tool result to message history
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result_content,
                    "is_error": is_error
                }]
            })
        else:
            # final response from claude
            return response.content[0].text

if __name__ == "__main__":

    # simple lookup
    print("=" * 70)
    print("Example: Getting NHL Player Stats with Function Calling")
    print("=" * 70)

    result = run_agent("What are Connor McDavid's stats this season?")
    print(f"\n[Claude's Response]\n{result}\n")

    # natural language query
    print("=" * 70)
    result = run_agent("How many goals has Auston Matthews scored?")
    print(f"\n[Claude's Response]\n{result}\n")

    print("=" * 70)
    print("\nKey Observations:")
    print("- We wrote custom glue code to connect the API to the LLM")
    print("- We manually defined the tool schema from API docs")
    print("- We handle the message loop ourselves")
    print("- Each API requires this same pattern repeated")
    print("\nWith MCP (see ex04_mcp_server.py):")
    print("- Tool definitions are automatic")
    print("- Message handling is built-in")
    print("- One server can expose multiple related tools")
    print("- Standard protocol across all integrations")