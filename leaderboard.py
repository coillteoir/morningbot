"""
    Leaderboard for morningbot
"""

import json
import os

class Member:
    def __init__(self, name, mornings):
        self.name = name
        self.mornings = mornings

class Leaderboard:
    def __init__(self, channel):
        path = "config/{}leaderboard.json".format(channel)
        self.members = []
        if os.path.isfile(path):
            fp = open(path, "r")
            leader_dict = json.loads(fp)
            self.channel = leader_dict["channel"]
            for x in leader_dict:
                self.members.append(Member(x["name"], x["mornings"]))
            
        else:
            self.channel = channel

