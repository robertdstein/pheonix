from snipergw.skymap import Skymap
from argparse import Namespace
import gwemopt.utils
import logging
import numpy as np
from snipergw.paths import gwemopt_dir, base_output_dir
import subprocess
import pandas as pd
from snipergw.model import PlanConfig

gwemopt_run_path = gwemopt_dir.joinpath("bin/gwemopt_run")
gwemopt_config_dir = gwemopt_dir.joinpath("config")
gwemopt_tiling_dir = gwemopt_dir.joinpath("tiling")

logger = logging.getLogger(__name__)


def run_gwemopt(
        skymap: Skymap,
        plan_config: PlanConfig
) -> pd.DataFrame:
    """
    I (RS) sincerely apologise for all the terrible coding sins that are committed here

    :param skymap: Skymap of event
    :param plan_config: Plan config
    :return: Schedule dataframe
    """

    output_dir = base_output_dir.joinpath(
        f"{skymap.event_name}/{plan_config.telescope}")
    gwemopt_output_dir = output_dir.joinpath("gwemopt")

    exposures = ",".join([str(plan_config.exposuretime)
                          for _ in plan_config.filters.split(",")])

    cmd = f"python {gwemopt_run_path} --telescopes {plan_config.telescope} " \
          f"--doTiles --doPlots --doSchedule --doSkymap --doMovie " \
          f"--timeallocationType powerlaw " \
          f"--scheduleType greedy -o '{gwemopt_output_dir}' " \
          f"--gpstime {skymap.gps_time()} " \
          f"--skymap {skymap.skymap_path} --filters {plan_config.filters} " \
          f"--exposuretimes {exposures} --doSingleExposure --doAlternatingFilters " \
          f"--tilingDir {gwemopt_tiling_dir} " \
          f"--doBalanceExposure --configDirectory {gwemopt_config_dir} " \
          f"--powerlaw_cl 0.9 --doMovie "

    # f"--tilesType ranked "

    if skymap.is_3d:
        cmd += "--do3D"

    if not plan_config.cache:
        logger.info(f"Running gwemopt with command '{cmd}'")
        subprocess.run(
            cmd, shell=True,
            stdout=subprocess.DEVNULL,
            check=True
        )
    else:
        logger.info("Using cached schedule")

    coverage = output_dir.joinpath("tiles_coverage.pdf")
    coverage.unlink(missing_ok=True)
    coverage.symlink_to(gwemopt_output_dir.joinpath('tiles_coverage.pdf'))

    logger.info(f"See coverage at {coverage}")

    schedule_path = gwemopt_output_dir.joinpath(
        f"schedule_{plan_config.telescope}.dat")

    schedule = pd.read_csv(
        schedule_path, sep=" ",
        names=["field", "ra", "dec", "tobs", "limmag",
               "texp", "prob", "airmass", "filter", "pid"]
    )
    schedule_csv_path = output_dir.joinpath("schedule.csv")
    schedule.to_csv(schedule_csv_path)
    logger.info(f"See schedule at {schedule_csv_path}")

    tot_prob = 0.

    all_fields = list(set(schedule["field"]))

    for field in all_fields:
        df = schedule[schedule["field"] == field]
        tot_prob += df["prob"].iloc[0]

    schedule_time = np.sum(schedule["texp"])/60./60.
    logger.info(f"Schedule covers {100.*tot_prob:.1f}% of probability "
                f"with {len(all_fields)} fields, "
                f"takes {schedule_time:.2g} hours using {len(schedule)} pointings "
                f"of {plan_config.exposuretime}s each, "
                f"and uses filters {plan_config.filters} .")

    return schedule

