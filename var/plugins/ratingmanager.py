import urllib.request
import json
import perl
import sys
import traceback
import sys

spads = perl.RatingManager

pluginVersion = '0.2'
requiredSpadsVersion = '0.12.29'

server_url = "https://server3.beyondallreason.info"
rating_url = f"{server_url}/teiserver/api/spads/get_rating"
balance_url = f"{server_url}/teiserver/api/spads/balance_battle"

def getVersion(pluginObject):
    return pluginVersion

def getRequiredSpadsVersion(pluginName):
    return requiredSpadsVersion

class RatingManager:
    def __init__(self, context):
        spads.slog("RatingManager plugin loaded (version %s)" % pluginVersion, 3)

    def updatePlayerSkill(self, playerSkill, accountId, modName, gameType):
        try:
            with urllib.request.urlopen(f"{rating_url}/{accountId}/{gameType}") as f:
                raw_data = f.read().decode('utf-8')
                data = json.loads(raw_data)

                return [1, data["rating_value"], data["uncertainty"]]
        except Exception as e:
            spads.slog("Unhandled exception: [updatePlayerSkill]" + str(sys.exc_info()
                       [0]) + "\n" + str(traceback.format_exc()), 0)
            return [1, 16.66, 8.33]

    def balanceBattle(self, players, bots, clanMode, nbTeams, teamSize):
        try:
            spadsConf = spads.getSpadsConf()
            data = urllib.parse.urlencode({
                "players": players,
                "bots": bots,
                "nbTeams": nbTeams,
                "teamSize": teamSize,
                "clanMode": clanMode,
                "balanceMode": spadsConf['balanceMode']
            })
            data = data.encode('ascii')

            with urllib.request.urlopen(balance_url, data) as f:
                raw_response = f.read().decode('utf-8')
                response_data = json.loads(raw_response)

                # The second method consists in returning an array reference containing the balance information instead of directly editing the \%players and \%bots parameters. The returned array must contain 3 items: the unbalance indicator (as defined in first method description above), the player assignation hash and the bot assignation hash. The player assignation hash and the bot assignation hash have exactly the same structure: the keys are the player/bot names and the values are hashes containing team and id items with the corresponding values for the balanced battle.
                # player_assign_hash = {
                #     "player1": {"team": 0, "id": 0},
                #     "player2": {"team": 0, "id": 0},
                #     "player3": {"team": 0, "id": 0},
                #     "player4": {"team": 0, "id": 0},
                # }

                # bot_assign_hash = {
                #     "bot1": {"team": 0, "id": 0},,
                #     "bot2": {"team": 0, "id": 0},,
                # }

                # unbalance_indicator = 0.5

                spads.slog("[balanceBattle] Data result = " +
                           str(response_data))

                if len(response_data) == 0:
                    return [-1, {}, {}]
                    return -1
                else:
                    return [
                        response_data.get("unbalance_indicator", -1),
                        response_data.get("player_assign_hash", {}),
                        response_data.get("bot_assign_hash", {})
                    ]
        except Exception as e:
            spads.slog("Unhandled exception: [balanceBattle]" + str(sys.exc_info()
                       [0]) + "\n" + str(traceback.format_exc()), 0)
            return -1
