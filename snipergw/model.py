"""
This module contains the pydantic models used to validate the input
"""
from pathlib import Path

from astropy import units as u
from astropy.time import Time
from pydantic import BaseModel, validator

from snipergw.paths import base_output_dir


class EventConfig(BaseModel):
    event: str | None = None
    rev: int | None = None
    output_dir: Path = base_output_dir


DEFAULT_TELESCOPE = "ZTF"
DEFAULT_FILTERS = "g,r,g"
DEFAULT_EXPOSURE = 300.0
DEFAULT_STARTTIME = Time.now() + 0.25 * u.hour

all_telescopes = [DEFAULT_TELESCOPE, "WINTER","DECam"]


class PlanConfig(BaseModel):
    output_dir: Path = base_output_dir
    telescope: str = DEFAULT_TELESCOPE
    filters: str = DEFAULT_FILTERS
    exposuretime: float = DEFAULT_EXPOSURE
    cache: bool = False
    starttime: Time = DEFAULT_STARTTIME
    subprogram: str = "EMGW"
    use_both_grids: bool = False

    @validator("telescope")
    def telescope_must_be_known(cls, v):
        if v not in all_telescopes:
            raise ValueError(f"telescope must be in {all_telescopes}")
        return v

    class Config:
        arbitrary_types_allowed = True
