# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# fujifilm.py - Alpaca API responders for Camera
# -----------------------------------------------------------------------------
#
# ASCOM Camera driver for Fujifilm Mirrorless Camera
#
# Description:	Implements ASCOM driver for Fujifilm Mirrorless camera.
#				Communicates using USB connection.
#
# Implements:	ASCOM Standard iCamera V4 interface
# Author:		(2025) Tony Veinberg <tony.veinberg@gmail.com>
#
# Edit Log:
#
# Date			Who	Vers	Description
# -----------	---	-----	-------------------------------------------------------
# 2025-Mar-29	TJV	0.0.1	Initial edit, created from ASCOM driver template
# ---------------------------------------------------------------------------------
#
# Python Compatibility: Requires Python 3.7 or later
# GitHub: https://github.com/tonyveinberg/alpaca-fujifilm-cameras
#
# ---------------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2024
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# ----------------------------------------------------------------------------------

import math
import datetime
import re
import asyncio
import ephem
from threading import Lock
from logging import Logger
from config import Config
#from exceptions import AstroModeError, AstroAlignmentError, WatchdogError
#from shr import deg2rad, rad2hr, rad2deg, hr2rad, deg2dms, hr2hms, clamparcsec, empty_queue

class Fujifilm:

    def __init__(self, logger: Logger):
        self._lock = Lock()
        self.name: str = 'device'
        self.logger = logger
        

# ----------------------------
# Fujifilm Connection Methods
# ----------------------------
    async def client():
        null