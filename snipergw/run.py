"""
This module contains the main function for running snipergw.
"""

import logging

import numpy as np

from snipergw.model import EventConfig, PlanConfig
from snipergw.plan import run_gwemopt
from snipergw.skymap import Skymap
from snipergw.submit import submit_too_winter, submit_too_ztf

logger = logging.getLogger(__name__)


def run_snipergw(
    event: EventConfig,
    plan_config: PlanConfig,
    gwemopt_args: list[str] | None = None,
    submit: bool = False,
    delete: bool = False,
):
    """
    Run snipergw

    :param event: event
    :param plan_config: plan configuration
    :param gwemopt_args: gwemopt arguments
    :param submit: submit the queue
    :param delete: delete the queue
    """

    if gwemopt_args is None:
        gwemopt_args = []

    skymap = Skymap(event_config=event)
    schedule = run_gwemopt(
        skymap=skymap, plan_config=plan_config, gwemopt_args=gwemopt_args
    )

    if np.sum([submit is True, delete is True]) > 0:
        if plan_config.telescope == "ZTF":
            submit_too_ztf(
                schedule,
                event_name=event.event,
                plan_config=plan_config,
                submit=submit,
                delete=delete,
            )
        elif plan_config.telescope == "WINTER":
            submit_too_winter(
                schedule,
                event_name=event.event,
                plan_config=plan_config,
                submit=submit,
                delete=delete,
            )
        else:
            raise NotImplementedError

    else:
        logger.info(
            "Rerun with the --submit flag to actually submit a ToO. "
            "You can additionally use the --cache flag to use the schedule "
            "which was just generated, rather than regenerating one from scratch."
        )
