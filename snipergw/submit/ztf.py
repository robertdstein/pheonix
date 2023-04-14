import pandas as pd
import os
from planobs.models import TooTarget
from snipergw.model import EventConfig
from planobs.api import Queue

ZTF_FILTER_MAP = {"g": 1, "r": 2, "i": 3}

def submit_too_ztf(
        schedule: pd.DataFrame,
        event_config: EventConfig,
        subprogram: str = "EMGW"
):
    """
    Submit a ToO to ZTF

    :param schedule: Schedule dataframe
    :param event_config: Event config
    :param subprogram: Subprogram name e.g EMGW
    :return: None
    """
    
    targets = []

    for i, row in schedule.iterrows():
        targets.append(TooTarget(
            request_id=i,
            field_id=row["field"],
            filter_id=ZTF_FILTER_MAP[row["filter"]],
            subprogram_name=f"ToO_{subprogram}",
            exposure_time=row["texp"],
        ))

    # get name of user from home directory
    user = os.path.basename(os.path.expanduser("~"))

    q = Queue(user=user)

    t_0 = min(schedule["tobs"])
    t_1 = max(schedule["tobs"])
    
    q.add_trigger_to_queue(
        targets=targets,
        trigger_name=f"ToO_{subprogram}_{event_config.name}",
        validity_window_start_mjd=t_0,
        validity_window_end_mjd=t_1,
    )

    print(targets)

