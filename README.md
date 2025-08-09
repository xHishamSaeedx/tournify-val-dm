# Tournify Valorant DM API

A system for managing Valorant deathmatch tournaments that automatically validates matches and generates leaderboards.

## How It Works

### Match Validation Process

The system automatically discovers and validates matches that players participated in:

1. **Player History Check**: The system looks at each player's recent match history (last 30 days) to find all matches they've played.

2. **Common Match Discovery**: The system automatically finds the match that at least 70% of the players share in their history. This means if most players were in the same match, the system will find it automatically.

3. **Match Details Verification**: Once the common match is found, the system checks if the match details match what was expected:

   - **Start Time**: The match must have started within 5 minutes of the expected time
   - **Map**: The match must have been played on the expected map

4. **Final Validation**: The validation only passes if both the player history check (70% threshold) and the match details verification succeed.

### Leaderboard Generation Process

The leaderboard system works in two main phases:

1. **Match Validation First**: Before creating a leaderboard, the system first validates the match using the same process described above. This ensures the match is legitimate and all players actually participated.

2. **Performance Ranking**: Once validation passes, the system:
   - Collects performance data (kills and combat scores) for all players in the match
   - Filters to only include the players from the original request
   - Ranks players by total kills (highest first)
   - Uses average combat score as a tiebreaker when kills are equal
   - Creates a final leaderboard showing each player's rank and performance

## Key Features

- **Automatic Match Discovery**: No need to provide specific match IDs - the system finds the correct match automatically
- **Player Verification**: Ensures at least 70% of players actually participated in the match
- **Time and Map Validation**: Verifies the match happened when and where expected
- **Performance Ranking**: Creates fair leaderboards based on kills and combat scores
- **Real Data Integration**: Uses actual Valorant match data from Riot's servers

## What This Solves

- **Tournament Integrity**: Prevents fake match submissions by verifying players actually participated
- **Host Errors**: Automatically finds the correct match even if the wrong match ID was recorded
- **Fair Competition**: Creates accurate leaderboards based on real performance data
- **Automation**: Eliminates manual match verification and leaderboard creation

## TODO

1. **Upgrade API Key**: Improve the API key system for better security and rate limiting
2. **Change Time Window**: Reduce match history check from 2 days to 30 minutes for more precise tournament validation
3. **Return Non-Participants**: Add functionality to return the list of players who were detected as not participating in the match
