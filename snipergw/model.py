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
DEFAULT_STARTTIME = Time.now() + 0.25 * u.hour

all_telescopes = [DEFAULT_TELESCOPE, "WINTER", "DECam"]


class TelescopeDefault(BaseModel):
    filters: str
    exposuretime: float
    all_filters: list[str]


ztf_default = TelescopeDefault(
    filters="g,r,g", exposuretime=300.0, all_filters=["g", "r", "i"]
)
winter_default = TelescopeDefault(
    filters="J", exposuretime=450.0, all_filters=["y", "J", "Hs"]
)


class PlanConfig(BaseModel):
    output_dir: Path = base_output_dir
    telescope: str = DEFAULT_TELESCOPE
    filters: str = None
    exposuretime: float = None
    cache: bool = False
    starttime: Time = DEFAULT_STARTTIME
    subprogram: str = "EMGW"
    use_both_grids: bool = False

    @validator("telescope")
    def telescope_must_be_known(cls, v):
        if v not in all_telescopes:
            raise ValueError(f"telescope must be in {all_telescopes}")
        return v

    @validator("filters", always=True)
    def set_default_filter(cls, field_value, values, field):
        if field_value is None:
            if values["telescope"] == "ZTF":
                return ztf_default.filters
            elif values["telescope"] == "WINTER":
                return winter_default.filters
            else:
                raise ValueError(f"Unknown telescope {values['telescope']}")

        for filter_name in field_value.split(","):
            if values["telescope"] == "ZTF":
                assert (
                    filter_name in ztf_default.all_filters
                ), f"Unknown filter {filter_name} for telescope {values['telescope']}, acceptable filters are {ztf_default.all_filters}"
            elif values["telescope"] == "WINTER":
                assert (
                    filter_name in winter_default.all_filters
                ), f"Unknown filter {filter_name} for telescope {values['telescope']}, acceptable filters are {winter_default.all_filters}"
            else:
                raise ValueError(f"Unknown telescope {values['telescope']}")

        return field_value

    @validator("exposuretime", always=True)
    def set_default_exposure(cls, field_value, values, field):
        if field_value is None:
            if values["telescope"] == "ZTF":
                return ztf_default.exposuretime
            elif values["telescope"] == "WINTER":
                return winter_default.exposuretime
            else:
                raise ValueError(f"Unknown telescope {values['telescope']}")

        return field_value

    class Config:
        arbitrary_types_allowed = True
