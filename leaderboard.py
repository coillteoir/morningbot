"""

LEADERBOARD CLASS FOR MORNING DISCORD BOT
David Lynch : https://github.com/davidlynch-sd

28-05-2023
"""

import os
import json

class LeaderBoard(object):
    def __init__(self, server):
        if os.path.isfile(os.path.join("leaderboards", server + ".json")):
            print("LEADERBOARD is REAL!!!!")
        else:
            print("LEADERBOARD is FAKE!!!!")
        #Read a config
        #If no config exists create one 

    def add(self, user):
        pass

    def __str__(self):
        pass
