"""
Module to plan observations with gwemopt
"""
import logging
import subprocess

import numpy as np
import pandas as pd
import pytz
from astropy.time import Time

from snipergw.model import PlanConfig
from snipergw.paths import base_output_dir, gwemopt_dir
from snipergw.skymap import Skymap

gwemopt_run_path = gwemopt_dir.joinpath("bin/gwemopt_run")
gwemopt_config_dir = gwemopt_dir.joinpath("config")
gwemopt_tiling_dir = gwemopt_dir.joinpath("tiling")


logger = logging.getLogger(__name__)

timezone_format = "%Y-%m-%dT%H:%M:%S"


def run_gwemopt(
    skymap: Skymap, plan_config: PlanConfig, gwemopt_args: list[str]
) -> pd.DataFrame:
    """
    I (RS) sincerely apologise for all the terrible coding sins that are committed here

    :param skymap: Skymap of event
    :param plan_config: Plan config
    :param gwemopt_args: List of arguments to pass to gwemopt
    :return: Schedule dataframe
    """

    output_dir = base_output_dir.joinpath(
        f"{skymap.event_name}/{plan_config.telescope}"
    )
    gwemopt_output_dir = output_dir.joinpath("gwemopt")

    exposures = ",".join(
        [str(plan_config.exposuretime) for _ in plan_config.filters.split(",")]
    )

    cmd = (
        f"python {gwemopt_run_path} --telescopes {plan_config.telescope} "
        f"--doTiles --doPlots --doSchedule --doSkymap "
        f"--timeallocationType powerlaw "
        f"--scheduleType greedy -o '{gwemopt_output_dir}' "
        f"--gpstime {plan_config.starttime.gps} "
        f"--skymap {skymap.skymap_path} --filters {plan_config.filters} "
        f"--exposuretimes {exposures} --doSingleExposure "
        f"--tilingDir {gwemopt_tiling_dir} "
        f"--doBalanceExposure --configDirectory {gwemopt_config_dir} "
        f"--powerlaw_cl 0.9 "
        f"--airmass 2.5 --mindiff 30 "
    )

    if not plan_config.telescope == "DECam":
        extra_cmd = "--doAlternatingFilters "
        cmd += extra_cmd

    if not plan_config.use_both_grids and plan_config.telescope == "ZTF":
        gwemopt_args.append("--doUsePrimary")

    if skymap.is_3d:
        gwemopt_args.append("--do3D")

    cmd += " ".join(gwemopt_args)

    if not plan_config.cache:
        logger.info(f"Running gwemopt with command '{cmd}'")
        subprocess.run(
            cmd,
            shell=True,
            # stdout=subprocess.DEVNULL,
            check=True,
        )
    else:
        logger.info("Using cached schedule")

    coverage = output_dir.joinpath("tiles_coverage.pdf")
    coverage.unlink(missing_ok=True)
    coverage.symlink_to(gwemopt_output_dir.joinpath("tiles_coverage.pdf"))

    movie = output_dir.joinpath("coverage.mpg")
    movie.unlink(missing_ok=True)
    movie.symlink_to(gwemopt_output_dir.joinpath("coverage.mpg"))

    logger.info(f"See coverage at {coverage}")

    schedule_path = gwemopt_output_dir.joinpath(f"schedule_{plan_config.telescope}.dat")

    schedule = pd.read_csv(
        schedule_path,
        sep=" ",
        names=[
            "field",
            "ra",
            "dec",
            "tobs",
            "limmag",
            "texp",
            "prob",
            "airmass",
            "filter",
            "pid",
        ],
    )

    mjds = Time(schedule["tobs"].to_numpy(), format="mjd")

    utcs = [x.tt.datetime.replace(tzinfo=pytz.utc) for x in mjds]

    schedule["utctime"] = [x.strftime(timezone_format) for x in utcs]

    # convert to time in Pacific time
    schedule["palomartime"] = [
        x.astimezone(pytz.timezone("America/Los_Angeles")).strftime(timezone_format)
        for x in utcs
    ]

    schedule_csv_path = output_dir.joinpath("schedule.csv")
    schedule.to_csv(schedule_csv_path)
    logger.info(f"See schedule at {schedule_csv_path}")

    tot_prob = 0.0

    all_fields = list(set(schedule["field"]))

    for field in all_fields:
        df = schedule[schedule["field"] == field]
        tot_prob += df["prob"].iloc[0]

    schedule_time = np.sum(schedule["texp"]) / 60.0 / 60.0
    logger.info(
        f"Schedule covers {100.*tot_prob:.1f}% of probability "
        f"with {len(all_fields)} fields, "
        f"takes {schedule_time:.2g} hours using {len(schedule)} pointings "
        f"of {plan_config.exposuretime}s each, "
        f"and uses filters {plan_config.filters} ."
    )

    return schedule
