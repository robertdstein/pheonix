from pydantic import BaseModel, validator
from pathlib import Path
from snipergw.paths import base_output_dir


class EventConfig(BaseModel):
    event: str | None = None
    rev: int | None = None
    output_dir: Path = base_output_dir


DEFAULT_TELESCOPE = "ZTF"
DEFAULT_FILTERS = "r,g,r"
DEFAULT_EXPOSURE = 300.

all_telescopes = [DEFAULT_TELESCOPE, "WINTER"]


class PlanConfig(BaseModel):
    output_dir: Path = base_output_dir
    telescope: str = DEFAULT_TELESCOPE
    filters: str = DEFAULT_FILTERS
    exposuretime: float = DEFAULT_EXPOSURE
    cache: bool = False

    @validator('telescope')
    def telescope_must_be_known(cls, v):
        if v not in all_telescopes:
            raise ValueError(f'telescope must be in {all_telescopes}')
        return v
