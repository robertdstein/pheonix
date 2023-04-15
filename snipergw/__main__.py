import argparse
import logging
import numpy as np

from astropy.time import Time
from astropy import units as u

from snipergw.skymap import Skymap
from snipergw.plan import run_gwemopt
from snipergw.model import EventConfig, PlanConfig, DEFAULT_TELESCOPE, DEFAULT_EXPOSURE, DEFAULT_FILTERS, DEFAULT_STARTTIME
from snipergw.submit import submit_too_ztf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    prog='snipergw',
    description='Simple Nodal Interface for Planning '
                'Electromagnetic Reconnaissance of Gravitational Waves',
)
parser.add_argument("-e", '--event')
parser.add_argument('-r', '--rev')
parser.add_argument('-o', '--outputdir')
parser.add_argument('-t', '--telescope', default=DEFAULT_TELESCOPE)
parser.add_argument("-f", "--filters", default=DEFAULT_FILTERS)
parser.add_argument("--exposuretime", default=DEFAULT_EXPOSURE)
parser.add_argument("--subprogram", default="EMGW")
parser.add_argument("-c", "--cache", default=False, action="store_true")
parser.add_argument("-s", "--submit", default=False, action="store_true")
parser.add_argument("-d", "--delete", default=False, action="store_true")
parser.add_argument("-st", "--starttime", default=None)
args = parser.parse_args()

if args.starttime is not None:
    args.starttime = Time(args.starttime, format="isot", scale="utc")
else:
    args.starttime = DEFAULT_STARTTIME

event = EventConfig(**args.__dict__)
plan_config = PlanConfig(**args.__dict__)

skymap = Skymap(event_config=event)
schedule = run_gwemopt(skymap=skymap, plan_config=plan_config)

if np.sum([args.submit is True, args.delete is True]) > 0:
    if args.telescope == "ZTF":
        submit_too_ztf(schedule, event_config=event, subprogram=args.subprogram,
                       submit=args.submit, delete=args.delete)
    else:
        raise NotImplementedError

else:
    logger.info("Rerun with the --submit flag to actually submit a ToO. "
                "You can additionally use the --cache flag to use the schedule "
                "which was just generated, rather than regenerating one from scratch.")
