from unittest import TestCase
import numpy as np
import NspUtils.RosterLabeler as labeler
from NspUtils.RosterMetadataExtractor import RosterMetadataExtractor


class TestRosterLabeler(TestCase):
    def setUp(self):
        pass


class TestEachFunction(TestRosterLabeler):
    def test_calc_chi_square_shift_req(self):
        single_track_chi = labeler.calc_chi_square_shift_req(staffing, True)
        twin_track_chi = labeler.calc_chi_square_shift_req(staffing_two_track, True)

        assert np.allclose(single_track_chi, [0.6, 6, 14.87878788, 0., 0.])
        assert np.allclose(twin_track_chi, [1.2, 12., 29.75757576, 0., 0.])
        pass

    def test_label_file(self):
        df = labeler.label_file("../test_data/netsoc-rosters/netsoc_2020-0-mip.json", is_training_data=True)
        print(df)
        pass


staffing = [
    [
        [
            [0, 0, 2], [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]
        ]
    ],
    [
        [[0, 0, 1], [1, 0, 0], [5, 0, 0], [5, 0, 0], [12, 0, 0]]
    ],
    [
        [[0, 0, 1], [15, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]]
    ],
    [
        [[0, 0, 1], [1, 0, 0], [1, 0, 0], [1, 0, 0], [0, 0, 1]]
    ]
]

staffing_two_track = [
    [
        [
            [0, 0, 2], [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]
        ],
        [
            [0, 0, 2], [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]
        ]
    ],
    [
        [
            [0, 0, 1], [1, 0, 0], [5, 0, 0], [5, 0, 0], [12, 0, 0]
        ],
        [
            [0, 0, 1], [1, 0, 0], [5, 0, 0], [5, 0, 0], [12, 0, 0]
        ]
    ],
    [
        [
            [0, 0, 1], [15, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]
        ],
        [
            [0, 0, 1], [15, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0]
        ]
    ],
    [
        [
            [0, 0, 1], [1, 0, 0], [1, 0, 0], [1, 0, 0], [0, 0, 1]
        ],
        [
            [0, 0, 1], [1, 0, 0], [1, 0, 0], [1, 0, 0], [0, 0, 1]
        ]
    ]
]
