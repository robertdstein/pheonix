"""
This module contains the paths to the data directories.
"""

import os
from pathlib import Path

base_output_dir = os.getenv("SNIPERGW_DIR", Path.home().joinpath("Data/snipergw/"))

gwemopt_dir = Path(__file__).parent.joinpath("gwemopt")
