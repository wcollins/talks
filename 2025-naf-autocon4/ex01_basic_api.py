# AutoCon4 - API Example
"""
Direct NHL API Example - Traditional Approach

This demonstrates the traditional way of calling APIs:
- Requires technical knowledge (player IDs)
- Manual integration for each use case
- Human-readable output formatting
- Simple, predictable, deterministic
"""
import requests
from typing import Optional
import json

def get_player_stats_api(player_id: int) -> Optional[dict]:
    """Direct API approach - I gotta know the exact player IDs ???"""

    try:
        response = requests.get(
            f"https://api-web.nhle.com/v1/player/{player_id}/landing",
            headers={"User-Agent": "MyApp/1.0"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        # extract current season stats
        current_season = data['featuredStats']['regularSeason']['subSeason']

        # extract player info
        player_name = f"{data.get('firstName', {}).get('default', '')} {data.get('lastName', {}).get('default', '')}"
        team = data.get('currentTeamAbbrev', 'Unknown')
        position = data.get('position', 'Unknown')

        # comprehensive stats
        return {
            # Player info
            "player_name": player_name,
            "team": team,
            "position": position,
            "games_played": current_season.get('gamesPlayed', 0),

            # scoring stats
            "goals": current_season.get('goals', 0),
            "assists": current_season.get('assists', 0),
            "points": current_season.get('points', 0),
            "shots": current_season.get('shots', 0),
            "shooting_pct": round(current_season.get('shootingPctg', 0) * 100, 1),

            # special teams
            "power_play_goals": current_season.get('powerPlayGoals', 0),
            "power_play_points": current_season.get('powerPlayPoints', 0),
            "shorthanded_goals": current_season.get('shorthandedGoals', 0),
            "shorthanded_points": current_season.get('shorthandedPoints', 0),

            # impact metrics
            "game_winning_goals": current_season.get('gameWinningGoals', 0),
            "ot_goals": current_season.get('otGoals', 0),
            "plus_minus": current_season.get('plusMinus', 0),

            # discipline
            "penalty_minutes": current_season.get('pim', 0)
        }

    except requests.RequestException as e:
        print(f"❌ API Error: {e}")
        print("TIP: Check your internet connection and that NHL API is available")
        return None
    except KeyError as e:
        print(f"❌ Data Error: {e}")
        print("TIP: Player ID may be invalid or API response structure changed")
        return None

def print_player_stats(stats: dict) -> None:
    """Pretty print them stats!"""

    print(f"\n{'='*60}")
    print(f"  {stats['player_name']} - {stats['team']} ({stats['position']})")
    print(f"{'='*60}")
    print(f"\n📊 BASIC STATS")
    print(f"  Games Played: {stats['games_played']}")
    print(f"  Goals: {stats['goals']}")
    print(f"  Assists: {stats['assists']}")
    print(f"  Points: {stats['points']}")
    print(f"  +/-: {stats['plus_minus']:+d}")

    print(f"\n🎯 SHOOTING")
    print(f"  Shots: {stats['shots']}")
    print(f"  Shooting %: {stats['shooting_pct']}%")

    print(f"\n⚡ SPECIAL TEAMS")
    print(f"  Power Play Goals: {stats['power_play_goals']}")
    print(f"  Power Play Points: {stats['power_play_points']}")
    print(f"  Shorthanded Goals: {stats['shorthanded_goals']}")
    print(f"  Shorthanded Points: {stats['shorthanded_points']}")

    print(f"\n🏆 IMPACT")
    print(f"  Game Winning Goals: {stats['game_winning_goals']}")
    print(f"  Overtime Goals: {stats['ot_goals']}")

    print(f"\n⚠️  DISCIPLINE")
    print(f"  Penalty Minutes: {stats['penalty_minutes']}")
    print(f"{'='*60}\n")

# usage - Connor McDavid (player ID: 8478402)
if __name__ == "__main__":
    if stats := get_player_stats_api(8478402):
        print_player_stats(stats)
    else:
        print("Failed to fetch stats")