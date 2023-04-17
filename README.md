
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
pre-commit install
```

Make sure not to miss the `--recurse-submodules` flag, as this is required to download the `gwemopt` submodule.

Sometimes, if you are using a conda environment, you might need to run `poetry install` twice.

Note for ARM-based macs: The install of `fiona` might fail if you do not have [gdal](https://gdal.org/) installed. In that case, consider using a `conda` and running `conda install -c conda-forge gdal` before running `poetry install`.

If you want to generate movies, you also need to install `ffmpeg`, which you can do via `brew install ffmpeg` or `conda install -c conda-forge ffmpeg`.

## Usage

To use this functionality, you must first configure the connection details. You need both an API token, and to know the address of the Kowalski host address. You can then set these as environment variables:

export KOWALSKI_API_TOKEN=...

To run sniper GW, you can do:

```python -m snipergw -e EVENTNAME```

## Options

* No event: snipergw will download the latest event from the LIGO graceDB
* Event name: snipergw will download the event with the given name from the LIGO graceDB
* URL: snipergw will download the event from the given URL
* GRB: snipergw will download the latest GRB from the GCN circular page (Fermi-GBM)
* Skymap name: if a skymap with ".fit" in its name is saved to ~/Data/snipergw/sky_maps, snipergw will use this skymap instead of downloading a new one

## Code contributiion guide

We use `pre-commit` to enforce code style. Please install it and run it before committing your code. 
We enforce the following code style:
* `black` for code formatting
* isort for import sorting

the `pre-commit` configuration is in `.pre-commit-config.yaml`. 

If your code does not meet the style requirements, the commit will fail but 
the scripts will then be fixed automatically.
You just need to `git add` the fixed files, and then commit again.

In general, we try and follow the 'PR' model of code development:

* `git clone` the repo
* `git checkout -b my-new-feature`
* make changes
* `git add my-changes`
* `git commit -m "my changes"`
* `git push origin my-new-feature`
* create a pull request on github
