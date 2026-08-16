import os
import unittest


class EnvConfigTests(unittest.TestCase):
    def test_runtime_config_reads_gemini_and_roast_settings(self):
        os.environ["GEMINI_API_KEY"] = "test-key"
        os.environ["GEMINI_MODEL"] = "gemini-2.0-flash-lite"
        os.environ["ROAST_SYSTEM_PROMPT"] = "Roast in a savage but playful style"

        import bot

        self.assertEqual(bot.GEMINI_API_KEY, "test-key")
        self.assertEqual(bot.GEMINI_MODEL, "gemini-2.0-flash-lite")
        self.assertEqual(bot.ROAST_SYSTEM_PROMPT, "Roast in a savage but playful style")


if __name__ == "__main__":
    unittest.main()
