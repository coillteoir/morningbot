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
        self.channel = channel
        path = f"config/{self.channel}leaderboard.json"
        print(path)

        self.members = []
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as leader_file:
                leader_dict = json.load(leader_file)
            self.channel = leader_dict["channel"]

            for member in leader_dict["members"]:
                self.members.append(self.Member(member["name"], member["mornings"]))
        else:
            self.channel = channel

    def __str__(self):
        value = f"CHANNEL {self.channel}\n"
        for member in self.members:
            value += str(member) + "\n"
        return value

    def add_point(self, name):
        for member in self.members:
            if member.name == name:
                member.mornings += 1
                print("exists", member)
                break
        else:
            self.members.append(self.Member(name, 1))
            print(f"Created: {name}")

    def dump_data(self):
        path = f"config/{self.channel}leaderboard.json"

        member_list = list(map(lambda x: x.__dict__, self.members))

        leader_dict = {"channel": self.channel, "members": member_list}

        with open(path, "w+", encoding="utf-8") as dump_file:
            json.dump(leader_dict, dump_file)
