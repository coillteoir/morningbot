"""
    Leaderboard for morningbot
"""

import json
import os


class Leaderboard:
    class Member:
        def __init__(self, name, mornings):
            self.name = name
            self.mornings = mornings
        def __str__(self):
            return f"NAME: {self.name} SCORE: {self.mornings}"

    def __init__(self, channel):
        print("LEADERBOARD INIT")
        path = "config/{}leaderboard.json".format(channel)
        print(path)

        self.members = []
        if os.path.isfile(path):
            with open(path, "r") as leader_file:
                leader_dict = json.loads(leader_file)
            self.channel = leader_dict["channel"]

            for x in leader_dict:
                self.members.append(self.Member(x["name"], x["mornings"]))
        else:
            self.channel = channel
    def add_point(self, name):
        for x in self.members:
            if x.name == name:
                x.mornings += 1
                print("exists", x)
                break
        else:
            self.members.append(self.Member(name, 1))
            for x in self.members:
                print("created", x)

    def dump_data(self):
        path = f"config/{self.channel}leaderboard.json"


