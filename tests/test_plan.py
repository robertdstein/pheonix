from pathlib import Path
from unittest import TestCase

import pandas as pd
from astropy.time import Time

from snipergw.model import EventConfig, PlanConfig
from snipergw.plan import run_gwemopt
from snipergw.skymap import Skymap

test_path = Path(__file__).parent.joinpath("testdata/test_schedule.csv")


class TestRun(TestCase):
    """
    Test the run function
    """

    def test_run_snipergw(self):
        event = EventConfig(
            event="S190425z",
            rev=2,
        )
        plan_config = PlanConfig(
            starttime=Time("2019-04-25T09:00:00", format="isot", scale="utc"),
        )

        skymap = Skymap(event_config=event)
        schedule = run_gwemopt(skymap=skymap, plan_config=plan_config, gwemopt_args=[])

        expected_schedule = pd.read_csv(test_path, index_col=0)

        # Uncomment to update the test data
        # schedule.to_csv(test_path)

        pd.testing.assert_frame_equal(
            schedule.reset_index(drop=True), expected_schedule.reset_index(drop=True)
        )
