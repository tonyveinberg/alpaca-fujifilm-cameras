
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# camera.py - Alpaca API responders for Camera
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

from falcon import Request, Response, HTTPBadRequest, before
from logging import Logger
from shr import PropertyResponse, MethodResponse, PreProcessRequest, \
                StateValue, get_request_field, to_bool
from exceptions import *        # Nothing but exception classes
from fujifilm import Fujifilm
import asyncio

logger: Logger = None

# ----------------------
# MULTI-INSTANCE SUPPORT
# ----------------------
# If this is > 0 then it means that multiple devices of this type are supported.
# Each responder on_get() and on_put() is called with a devnum parameter to indicate
# which instance of the device (0-based) is being called by the client. Leave this
# set to 0 for the simple case of controlling only one instance of this device type.
#
maxdev = 0                      # Single instance

# -----------
# DEVICE INFO
# -----------
# Static metadata not subject to configuration changes
## EDIT FOR YOUR DEVICE ##
class CameraMetadata:
    """ Metadata describing the Camera Device. Edit for your device"""
    Name = 'Fujifilm Camera'
    Version = '0.0.1'
    Description = 'Alpaca ASCOM Driver for Fujifilm Cameras'
    DeviceType = 'Camera'
    DeviceID = 'd0858d19-b774-4853-821d-2eb1343c37a0' # https://guidgenerator.com/online-guid-generator.aspx
    Info = 'Alpaca Sample Device\nImplements ICamera\nASCOM Initiative'
    MaxDeviceNumber = maxdev
    InterfaceVersion = 4        # ICameraVxxx

# --------------
# SYMBOLIC ENUMS
# --------------
#
from enum import IntEnum

class CameraStates(IntEnum):
    cameraIdle      = 0,
    cameraWaiting   = 1,
    cameraExposing  = 2,
    cameraReading   = 3,
    cameraDownload  = 4,
    cameraError     = 5

class SensorType(IntEnum):
    Monochrome      = 0,
    Color           = 1,
    RGGB            = 2,
    CMYG            = 3,
    CMYG2           = 4,
    LRGB            = 5

class ImageArrayElementTypes(IntEnum):
    Unknown         = 0
    Int16           = 1
    Int32           = 2
    Double          = 3
    Single          = 4,
    UInt64          = 5,
    Byte            = 6,
    Int64           = 7,
    UInt16          = 8

# --------------------------------------------------------------------
# Create an instance of the Fujifilm Class to simulate an ASCOM camera
# --------------------------------------------------------------------
fujifilm = None
def start_fujifilm(logger: Logger):
    global fujifilm
    fujifilm = Fujifilm(logger)

# --------------------
# RESOURCE CONTROLLERS
# --------------------

#@before(PreProcessRequest(maxdev))
#class action:
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        resp.text = MethodResponse(req, NotImplementedException()).json
#
#@before(PreProcessRequest(maxdev))
#class commandblind:
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        resp.text = MethodResponse(req, NotImplementedException()).json
#
#@before(PreProcessRequest(maxdev))
#class commandbool:
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        resp.text = MethodResponse(req, NotImplementedException()).json
#
#@before(PreProcessRequest(maxdev))
#class commandstring:
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        resp.text = MethodResponse(req, NotImplementedException()).json
#
#@before(PreProcessRequest(maxdev))
#class connect:
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        try:
#            # ------------------------
#            ### CONNECT THE DEVICE ###
#            # ------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Connect failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class connected:
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        try:
#            # -------------------------------------
#            is_conn = ### READ CONN STATE ###
#            # -------------------------------------
#            resp.text = PropertyResponse(is_conn, req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req, DriverException(0x500, 'Camera.Connected failed', ex)).json
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        conn_str = get_request_field('Connected', req)
#        conn = to_bool(conn_str)              # Raises 400 Bad Request if str to bool fails
#
#        try:
#            # --------------------------------------
#            ### CONNECT OR DISCONNECT THE DEVICE ###
#            # --------------------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req, # Put is actually like a method :-(
#                            DriverException(0x500, 'Camera.Connected failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class connecting:
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        try:
#            # ------------------------------
#            val = ## GET CONNECTING STATE ##
#            # ------------------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Connecting failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class description:
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        resp.text = PropertyResponse(CameraMetadata.Description, req).json
#
#@before(PreProcessRequest(maxdev))
#class devicestate:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        try:
#            # ----------------------
#            val = []
#            # val.append(StateValue('## NAME ##', ## GET VAL ##))
#            # Repeat for each of the operational states per the device spec
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'camera.Devicestate failed', ex)).json
#
#
#class disconnect:
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        try:
#            # ---------------------------
#            ### DISCONNECT THE DEVICE ###
#            # ---------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Disconnect failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class driverinfo:
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        resp.text = PropertyResponse(CameraMetadata.Info, req).json
#
#@before(PreProcessRequest(maxdev))
#class interfaceversion:
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        resp.text = PropertyResponse(CameraMetadata.InterfaceVersion, req).json
#
#@before(PreProcessRequest(maxdev))
#class driverversion():
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        resp.text = PropertyResponse(CameraMetadata.Version, req).json
#
#@before(PreProcessRequest(maxdev))
#class name():
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        resp.text = PropertyResponse(CameraMetadata.Name, req).json
#
#@before(PreProcessRequest(maxdev))
#class supportedactions:
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        resp.text = PropertyResponse([], req).json  # Not PropertyNotImplemented
#
#@before(PreProcessRequest(maxdev))
#class bayeroffsetx:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Bayeroffsetx failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class bayeroffsety:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Bayeroffsety failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class binx:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Binx failed', ex)).json
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        binxstr = get_request_field('BinX', req)      # Raises 400 bad request if missing
#        try:
#            binx = int(binxstr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'BinX {binxstr} not a valid integer.')).json
#            return
#        ### RANGE CHECK AS NEEDED ###  # Raise Alpaca InvalidValueException with details!
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Binx failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class biny:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Biny failed', ex)).json
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        binystr = get_request_field('BinY', req)      # Raises 400 bad request if missing
#        try:
#            biny = int(binystr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'BinY {binystr} not a valid integer.')).json
#            return
#        ### RANGE CHECK AS NEEDED ###  # Raise Alpaca InvalidValueException with details!
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Biny failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class camerastate:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Camerastate failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class cameraxsize:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Cameraxsize failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class cameraysize:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Cameraysize failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class canabortexposure:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Canabortexposure failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class canasymmetricbin:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Canasymmetricbin failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class canfastreadout:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Canfastreadout failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class cangetcoolerpower:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Cangetcoolerpower failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class canpulseguide:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Canpulseguide failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class cansetccdtemperature:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Cansetccdtemperature failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class canstopexposure:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Canstopexposure failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class ccdtemperature:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Ccdtemperature failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class cooleron:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Cooleron failed', ex)).json
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        cooleronstr = get_request_field('CoolerOn', req)      # Raises 400 bad request if missing
#        try:
#            cooleron = to_bool(cooleronstr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'CoolerOn {cooleronstr} not a valid boolean.')).json
#            return
#
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Cooleron failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class coolerpower:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Coolerpower failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class electronsperadu:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Electronsperadu failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class exposuremax:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Exposuremax failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class exposuremin:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Exposuremin failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class exposureresolution:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Exposureresolution failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class fastreadout:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Fastreadout failed', ex)).json
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        fastreadoutstr = get_request_field('FastReadout', req)      # Raises 400 bad request if missing
#        try:
#            fastreadout = to_bool(fastreadoutstr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'FastReadout {fastreadoutstr} not a valid boolean.')).json
#            return
#
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Fastreadout failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class fullwellcapacity:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Fullwellcapacity failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class gain:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Gain failed', ex)).json
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        gainstr = get_request_field('Gain', req)      # Raises 400 bad request if missing
#        try:
#            gain = int(gainstr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'Gain {gainstr} not a valid integer.')).json
#            return
#        ### RANGE CHECK AS NEEDED ###  # Raise Alpaca InvalidValueException with details!
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Gain failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class gainmax:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Gainmax failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class gainmin:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Gainmin failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class gains:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Gains failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class hasshutter:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Hasshutter failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class heatsinktemperature:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Heatsinktemperature failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class imagearray:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Imagearray failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class imagearrayvariant:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Imagearrayvariant failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class imageready:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Imageready failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class ispulseguiding:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Ispulseguiding failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class lastexposureduration:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Lastexposureduration failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class lastexposurestarttime:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Lastexposurestarttime failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class maxadu:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Maxadu failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class maxbinx:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Maxbinx failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class maxbiny:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Maxbiny failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class numx:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Numx failed', ex)).json
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        numxstr = get_request_field('NumX', req)      # Raises 400 bad request if missing
#        try:
#            numx = int(numxstr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'NumX {numxstr} not a valid integer.')).json
#            return
#        ### RANGE CHECK AS NEEDED ###  # Raise Alpaca InvalidValueException with details!
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Numx failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class numy:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Numy failed', ex)).json
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        numystr = get_request_field('NumY', req)      # Raises 400 bad request if missing
#        try:
#            numy = int(numystr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'NumY {numystr} not a valid integer.')).json
#            return
#        ### RANGE CHECK AS NEEDED ###  # Raise Alpaca InvalidValueException with details!
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Numy failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class offset:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Offset failed', ex)).json
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        offsetstr = get_request_field('Offset', req)      # Raises 400 bad request if missing
#        try:
#            offset = int(offsetstr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'Offset {offsetstr} not a valid integer.')).json
#            return
#        ### RANGE CHECK AS NEEDED ###  # Raise Alpaca InvalidValueException with details!
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Offset failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class offsetmax:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Offsetmax failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class offsetmin:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Offsetmin failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class offsets:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Offsets failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class percentcompleted:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Percentcompleted failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class pixelsizex:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Pixelsizex failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class pixelsizey:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Pixelsizey failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class readoutmode:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Readoutmode failed', ex)).json
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        readoutmodestr = get_request_field('ReadoutMode', req)      # Raises 400 bad request if missing
#        try:
#            readoutmode = int(readoutmodestr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'ReadoutMode {readoutmodestr} not a valid integer.')).json
#            return
#        ### RANGE CHECK AS NEEDED ###  # Raise Alpaca InvalidValueException with details!
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Readoutmode failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class readoutmodes:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Readoutmodes failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class sensorname:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Sensorname failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class sensortype:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Sensortype failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class setccdtemperature:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Setccdtemperature failed', ex)).json
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        setccdtemperaturestr = get_request_field('SetCCDTemperature', req)      # Raises 400 bad request if missing
#        try:
#            setccdtemperature = float(setccdtemperaturestr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'SetCCDTemperature {setccdtemperaturestr} not a valid number.')).json
#            return
#        ### RANGE CHECK AS NEEDED ###  # Raise Alpaca InvalidValueException with details!
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Setccdtemperature failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class startx:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Startx failed', ex)).json
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        startxstr = get_request_field('StartX', req)      # Raises 400 bad request if missing
#        try:
#            startx = int(startxstr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'StartX {startxstr} not a valid integer.')).json
#            return
#        ### RANGE CHECK AS NEEDED ###  # Raise Alpaca InvalidValueException with details!
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Startx failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class starty:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Starty failed', ex)).json
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        startystr = get_request_field('StartY', req)      # Raises 400 bad request if missing
#        try:
#            starty = int(startystr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'StartY {startystr} not a valid integer.')).json
#            return
#        ### RANGE CHECK AS NEEDED ###  # Raise Alpaca InvalidValueException with details!
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Starty failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class subexposureduration:
#
#    def on_get(self, req: Request, resp: Response, devnum: int):
#        if not ##IS DEV CONNECTED##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # ----------------------
#            val = ## GET PROPERTY ##
#            # ----------------------
#            resp.text = PropertyResponse(val, req).json
#        except Exception as ex:
#            resp.text = PropertyResponse(None, req,
#                            DriverException(0x500, 'Camera.Subexposureduration failed', ex)).json
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        subexposuredurationstr = get_request_field('SubExposureDuration', req)      # Raises 400 bad request if missing
#        try:
#            subexposureduration = float(subexposuredurationstr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'SubExposureDuration {subexposuredurationstr} not a valid number.')).json
#            return
#        ### RANGE CHECK AS NEEDED ###  # Raise Alpaca InvalidValueException with details!
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Subexposureduration failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class abortexposure:
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Abortexposure failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class pulseguide:
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        directionstr = get_request_field('Direction', req)      # Raises 400 bad request if missing
#        try:
#            direction = int(directionstr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'Direction {directionstr} not a valid integer.')).json
#            return
#        if not direction in [0, 1, 2, 3]:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'Direction {direction} not a valid enum value.')).json
#            return
#
#        durationstr = get_request_field('Duration', req)      # Raises 400 bad request if missing
#        try:
#            duration = int(durationstr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'Duration {durationstr} not a valid integer.')).json
#            return
#        ### RANGE CHECK AS NEEDED ###  # Raise Alpaca InvalidValueException with details!
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Pulseguide failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class startexposure:
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        durationstr = get_request_field('Duration', req)      # Raises 400 bad request if missing
#        try:
#            duration = float(durationstr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'Duration {durationstr} not a valid number.')).json
#            return
#        ### RANGE CHECK AS NEEDED ###  # Raise Alpaca InvalidValueException with details!
#        lightstr = get_request_field('Light', req)      # Raises 400 bad request if missing
#        try:
#            light = to_bool(lightstr)
#        except:
#            resp.text = MethodResponse(req,
#                            InvalidValueException(f'Light {lightstr} not a valid boolean.')).json
#            return
#
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Startexposure failed', ex)).json
#
#@before(PreProcessRequest(maxdev))
#class stopexposure:
#
#    def on_put(self, req: Request, resp: Response, devnum: int):
#        if not ## IS DEV CONNECTED ##:
#            resp.text = PropertyResponse(None, req,
#                            NotConnectedException()).json
#            return
#        
#        try:
#            # -----------------------------
#            ### DEVICE OPERATION(PARAM) ###
#            # -----------------------------
#            resp.text = MethodResponse(req).json
#        except Exception as ex:
#            resp.text = MethodResponse(req,
#                            DriverException(0x500, 'Camera.Stopexposure failed', ex)).json

