import tempfile,unittest
from pathlib import Path
from tests.manual.v2.suite_plan import ROOT
from tests.manual.v2.remote_runtime_probe import replay_recipe
from voice_stt_client.core.v2_runtime import runtime_profile


class Recipe(unittest.TestCase):
    def test_saved_recipe_and_runtime_migration_snapshot_agree(self):
        for mode in ('manual','wake','both'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory(dir=ROOT/'build',prefix='recipe-check-') as folder:
                cfg=replay_recipe(Path(folder),mode);profile=runtime_profile(cfg)
                self.assertEqual(profile.desired_settings['wakeWord.preRollMs'],320)
                self.assertEqual(profile.desired_settings['activation.followupTimeoutMs'],5000)
                self.assertEqual(profile.manual,mode!='wake')
                self.assertEqual(profile.wake_word,mode!='manual')
