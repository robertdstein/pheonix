
# SniperGW

## Simple Nodal Interface for Planning Electromagnetic Reconnaissance of Gravitational Waves (SniperGW)


`snipergw` is a simple python package to glue together existing emgw tools.
Specifically it does three things:
* Downloads fits files, e.g via ligo-gracedb to download GW events, GRB events via web scraping, or from a URL
* Uses gwemopt to generate an observation schedule
* Actually submits these schedules to either ZTF or WINTER via APIs

## Installation

We suggest using a conda environment to install `snipergw`, with python>=3.10.
You can then install the package using `pip` and `poetry`:

```
git clone --recurse-submodules git@github.com:robertdstein/snipergw.git
cd snipergw
pip install poetry
poetry install
```

Make sure not to miss the `--recurse-submodules` flag, as this is required to download the `gwemopt` submodule.

Note for ARM-based macs: The install of `fiona` might fail if you do not have [gdal](https://gdal.org/) installed. In that case, consider using a `conda` and running `conda install -c conda-forge gdal` before running `poetry install`.

To use this functionality, you must first configure the connection details. You need both an API token, and to know the address of the Kowalski host address. You can then set these as environment variables:

export KOWALSKI_API_TOKEN=...