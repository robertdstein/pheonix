"""
This module contains the Skymap class, which downloads and parses a skymap
"""

import logging

#!/usr/bin/env python
# coding: utf-8
import os
from pathlib import Path

import lxml.etree
import numpy as np
import requests
import wget
from astropy.io import fits
from astropy.time import Time
from ligo.gracedb.rest import GraceDb
from lxml import html

from snipergw.model import EventConfig

logger = logging.getLogger(__name__)


class Skymap:
    """
    Skymap Handler class
    """

    def __init__(self, event_config: EventConfig):
        """
        Download a skymap

        :param event_config: event
        """

        event_name = event_config.event

        self.base_skymap_dir = event_config.output_dir.joinpath(f"skymaps")
        self.base_skymap_dir.mkdir(parents=True, exist_ok=True)

        self.is_3d = False

        if event_name is None:
            self.skymap_path, self.event_name = self.get_gw_skymap(
                event_name=event_name, rev=event_config.rev
            )
            self.is_3d = True
        elif ".fit" in event_name:
            self.skymap_path, self.event_name = self.parse_fits_file(event_name)
        elif np.sum([x in str(event_config.event) for x in ["s", "S", "gw", "GW"]]) > 0:
            self.skymap_path, self.event_name = self.get_gw_skymap(
                event_name=event_name, rev=event_config.rev
            )
            self.is_3d = True
        elif "grb" in event_name or "GRB" in event_name:
            self.skymap_path, self.event_name = self.get_grb_skymap(
                event_name=event_name
            )
        else:
            raise Exception(
                f"Event {event_name} not recognised as a fits file, "
                f"a GRB or a GW event."
            )

        logger.info(f"Unpacking skymap for event {self.event_name}")

        self.t_obs = self.read_map()

    def parse_fits_file(self, event: str):
        """
        Parse a fits file event

        :param event: Fits file name or URL
        :return: Fits path, name
        """

        basename = os.path.basename(event)

        skymap_path = self.base_skymap_dir.joinpath(basename)

        if skymap_path.exists():
            event_name = basename

        elif event[:8] == "https://":
            logger.info(f"Downloading from: {event}")
            skymap_path = self.base_skymap_dir.joinpath(os.path.basename(event[7:]))
            wget.download(event, str(skymap_path))
            event_name = os.path.basename(event[7:])
        else:
            raise FileNotFoundError(f"Unrecognised file {skymap_path}")

        return skymap_path, event_name

    def get_grb_skymap(self, event_name: str):
        """
        Function to download GRB from GCN

        :param event_name: Name of GRB
        :return: Fits path, event name
        """
        if event_name is None:
            raise ValueError(
                "event_name must be provided for GRBs. "
                "They must have the form 'GRB210729A"
            )

        event_name = event_name.upper().replace(" ", "")

        event_year_short = event_name[3:5]
        event_year = "20" + event_year_short
        event_month = event_name[5:7]
        event_day = event_name[7:9]
        event_letter = event_name[9].upper()
        event_number = ord(event_letter) - 65

        # get possible skymap URLs
        url = f"https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/{event_year}"

        page_overview = requests.get(url)
        webpage_overview = html.fromstring(page_overview.content)

        links_overview = webpage_overview.xpath("//a/@href")

        links_for_date = []

        for link in links_overview:
            if link[2:8] == f"{event_year_short}{event_month}{event_day}":
                links_for_date.append(url + "/" + link + "current/")

        if len(links_for_date) > 1:
            logger.info(
                f"Found multiple events. "
                f"Will choose the one corresponding the GRB letter {event_letter}"
            )

        event_url = links_for_date[event_number]

        page_event = requests.get(event_url)
        webpage_event = html.fromstring(page_event.content)
        links_event = webpage_event.xpath("//a/@href")

        for link in links_event:
            if "glg_healpix" in link:
                final_link = event_url + link
                break

        skymap_path = self.base_skymap_dir.joinpath(link)

        if skymap_path.exists():
            logger.info(f"Continuing with saved skymap. Located at {skymap_path}")
        else:
            logger.info(f"Downloading skymap and saving to {skymap_path}")
            wget.download(final_link, str(skymap_path))

        self.event_name = event_name
        return skymap_path, event_name

    def get_gw_skymap(self, event_name: str, rev: int) -> [Path, str]:
        """
        Function to download GW event from GraceDB

        :param event_name: Name e.g S200316bj
        :param rev: Revision number
        :return: Fits path, event name
        """

        ligo_client = GraceDb()

        logger.info("Obtaining skymap from GraceDB")

        if event_name is None:
            superevent_iterator = ligo_client.superevents("category: Production")
            superevent_ids = [
                superevent["superevent_id"] for superevent in superevent_iterator
            ]
            event_name = superevent_ids[0]

        voevents = ligo_client.voevents(event_name).json()["voevents"]

        if rev is None:
            rev = len(voevents)

        elif rev > len(voevents):
            raise Exception("Revision {0} not found".format(rev))

        latest_voevent = voevents[rev - 1]
        logger.info(f"Found voevent {latest_voevent['filename']}")

        if "Retraction" in latest_voevent["filename"]:
            raise ValueError(
                f"The specified LIGO event, "
                f"{latest_voevent['filename']}, was retracted."
            )

        response = requests.get(latest_voevent["links"]["file"])

        root = lxml.etree.fromstring(response.content)
        params = {
            elem.attrib["name"]: elem.attrib["value"]
            for elem in root.iterfind(".//Param")
        }

        latest_skymap = params["skymap_fits"]

        logger.info(f"Latest skymap URL: {latest_skymap}")

        base_file_name = os.path.basename(latest_skymap)
        savepath = self.base_skymap_dir.joinpath(
            f"{event_name}_{latest_voevent['N']}_{base_file_name}",
        )

        if savepath.exists():
            logger.info(f"File {savepath} already exists. Using this.")
        else:
            logger.info(f"Saving to: {savepath}")
            response = requests.get(latest_skymap)

            with open(savepath, "wb") as f:
                f.write(response.content)

        return savepath, event_name

    def read_map(
        self,
    ) -> Time:
        """
        Function to read skymap

        :return: Time of skymap detection
        """

        logger.info(f"Reading file: {self.skymap_path}")

        with fits.open(self.skymap_path) as hdul:
            for x in hdul:
                if "DATE-OBS" in x.header:
                    t_obs = Time(x.header["DATE-OBS"], format="isot")

                elif "EVENTMJD" in x.header:
                    t_obs_mjd = x.header["EVENTMJD"]
                    t_obs = Time(t_obs_mjd, format="mjd")

        return t_obs
