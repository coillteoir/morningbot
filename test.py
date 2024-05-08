import unittest

import bot


class TestBot(unittest.TestCase):
    def test_config(self):
        bot_test = bot.Bot("config/configuration_data.json")
        self.assertNotEqual(bot_test, None)
