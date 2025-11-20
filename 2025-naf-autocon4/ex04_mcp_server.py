"""
MCP Server for NHL Player Statistics

Demonstrates how MCP eliminates custom glue code, manual
tool definitions, and message handling.

Architecture:
- FastMCP server exposes tools via decorators
- stdio transport for Claude Desktop integration
- Automatic tool registration and schema generation
- Built-in message handling (no custom agent loop)
"""

import requests
from typing import Optional
from functools import lru_cache
from mcp.server.fastmcp import FastMCP

# initialize MCP server
mcp = FastMCP("nhl-stats")


@lru_cache(maxsize=128)
def lookup_player_id(player_name: str) -> Optional[int]:
    """
    Convert player name to NHL player ID using search API.

    Cached to avoid repeated lookups for the same player. This is a common
    pattern: one API call to discover identifiers, then another to fetch data.

    Args:
        player_name: Full or partial player name (e.g., "Connor McDavid")

    Returns:
        Player ID if found, None otherwise
    """
    url = "https://search.d3.nhle.com/api/v1/search/player"
    headers = {"User-Agent": "MCPServer/1.0"}

    try:
        response = requests.get(
            url,
            params={"culture": "en-us", "q": player_name},
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        data = response.json()

        if data and len(data) > 0:
            player_id = data[0].get("playerId")

            # API returns playerId as string, convert to int
            return int(player_id) if player_id else None
        return None
    except Exception as e:
        print(f"Error looking up player: {e}")
        return None


@mcp.tool()
def get_player_stats(player_name: str) -> dict:
    """
    Get current season statistics for an NHL player by name.

    Returns comprehensive stats including goals, assists, points, shooting percentage,
    special teams performance, game-winning goals, and more. Automatically handles
    player name lookup and ID conversion.

    Args:
        player_name: Full or partial player name (e.g., "Connor McDavid", "McDavid")

    Returns:
        Dictionary with 17 stats across 5 categories:
        - Player info: name, team, position, games_played
        - Scoring: goals, assists, points, shots, shooting_pct
        - Special teams: power_play_goals, power_play_points, shorthanded_goals, shorthanded_points
        - Impact: game_winning_goals, ot_goals, plus_minus
        - Discipline: penalty_minutes

    Raises:
        ValueError: If player is not found or stats cannot be fetched
    """

    # convert name to player ID
    player_id = lookup_player_id(player_name)
    if not player_id:
        raise ValueError(f"Player '{player_name}' not found")

    # fetch stats
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    headers = {"User-Agent": "MCPServer/1.0"}

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
            "team": data.get("currentTeamAbbrev", "Unknown"),
            "position": data.get("position", "Unknown"),
            "games_played": season_totals.get("gamesPlayed", 0),
            "goals": season_totals.get("goals", 0),
            "assists": season_totals.get("assists", 0),
            "points": season_totals.get("points", 0),
            "shots": season_totals.get("shots", 0),
            "shooting_pct": round(season_totals.get("shootingPctg", 0) * 100, 1),
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


@mcp.tool()
def compare_players(player1_name: str, player2_name: str) -> dict:
    """
    Compare current season statistics between two NHL players.

    Fetches stats for both players and returns a side-by-side comparison with
    differences highlighted. Shows who's leading in each statistical category.

    Args:
        player1_name: First player's full or partial name (e.g., "Connor McDavid")
        player2_name: Second player's full or partial name (e.g., "Auston Matthews")

    Returns:
        Dictionary containing:
        - player1: Complete stats for first player
        - player2: Complete stats for second player
        - comparison: Category-by-category breakdown showing who leads and by how much

    Raises:
        ValueError: If either player is not found or stats cannot be fetched
    """

    # fetch stats for both players
    player1_stats = get_player_stats(player1_name)
    player2_stats = get_player_stats(player2_name)

    # build comparison for numeric stats
    comparison = {}
    numeric_fields = [
        "games_played", "goals", "assists", "points", "shots", "shooting_pct",
        "power_play_goals", "power_play_points", "shorthanded_goals",
        "shorthanded_points", "game_winning_goals", "ot_goals", "plus_minus",
        "penalty_minutes"
    ]

    for field in numeric_fields:
        p1_val = player1_stats.get(field, 0)
        p2_val = player2_stats.get(field, 0)
        difference = p1_val - p2_val

        comparison[field] = {
            player1_stats["player_name"]: p1_val,
            player2_stats["player_name"]: p2_val,
            "difference": difference,
            "leader": player1_stats["player_name"] if difference > 0 else
                     player2_stats["player_name"] if difference < 0 else "tied"
        }

    return {
        "player1": player1_stats,
        "player2": player2_stats,
        "comparison": comparison
    }


if __name__ == "__main__":

    # run server with stdio transport for Claude Desktop
    mcp.run()