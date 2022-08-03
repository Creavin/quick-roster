from unittest import TestCase
import pandas as pd
from NspUtils.RosterMetadataExtractor import RosterMetadataExtractor


class TestObjectiveScoreExtractor(TestCase):
    def setUp(self):
        self.extractor = RosterMetadataExtractor
        pass


class TestEachFunction(TestObjectiveScoreExtractor):
    def test_extract_scores(self):
        df = self.extractor.extract_scores()
        assert type(df) == pd.core.frame.DataFrame
        pass
