Simple Nodal Interface for Planning Electromagnetic Reconnaissance of Gravitational Waves (SniperGW)

`pip install poetry`
`poetry install`

`snipergw` is a simple python package to glue together existing emgw tools.
Specifically it does three things:
* Downloads fits files, e.g via ligo-gracedb to download GW events, GRB events via web scraping, or from a URL
* Uses gwemopt to generate an observation schedule
* Actually submits these schedules to either ZTF or WINTER via APIs