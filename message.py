import pyModeS as pms

class ModeSMessage:
    """
    A decoded Mode S message.

    All subclasses have the following fields present, though some may be
    set to None:

      DF: downlink format
      address: ICAO address of transmitting aircraft. For some message types
        this is derived from the CRC field and may be unreliable.
      altitude: decoded altitude in feet, or None if not present / not available
      callsign: decoded callsign, or None if not present
      squawk: decoded squawk, or None if not present
      crc_ok: True if the CRC is OK. False if it is bad. None if the correctness
        of the CRC cannot be checked (e.g. the messages uses AP or PI)
    """

class DF0(ModeSMessage):
    """
    DF0 (Short air-air surveillance / ACAS) message.

    Fields: DF, VS, CC, SL, RI, AC, altitude, address
    """

    def __init__(self, pkt):
        self.DF = pms.common.df(pkt['hexStr'])
        self.ICAO = pms.common.icao(pkt['hexStr'])
        self.indice = pkt['indice']
        self.altitude = pms.common.altcode(pkt['hexStr'])
        self.crc_ok = None
        self.squawk = self.callsign = None

class DF4(ModeSMessage):
    """
    DF4 (Surveillance, altitude reply) message.

    Fields: DF, FS, DR, UM, AC, altitude, address
    """
    def __init__(self, pkt):
        self.DF = pms.common.df(pkt['hexStr'])
        self.ICAO = pms.common.icao(pkt['hexStr'])
        self.indice = pkt['indice']
        self.altitude = pms.common.altcode(pkt['hexStr'])
        self.crc_ok = None
        self.squawk = self.callsign = None

class DF5(ModeSMessage):
    """
    DF5 (Surveillance, identity reply) message.

    Fields: DF, FS, DR, UM, ID, squawk, address
    """
    def __init__(self, pkt):
        self.DF = pms.common.df(pkt['hexStr'])
        self.ICAO = pms.common.icao(pkt['hexStr'])
        self.indice = pkt['indice']
        self.squawk = pms.common.idcode(pkt['hexStr'])
        self.crc_ok = None
        self.altitude = self.callsign = None

class DF11(ModeSMessage):
    """
    DF11 (All-call reply) message.

    Fields: DF, CA, AA, address, crc_ok
    """
    def __init__(self, pkt):
        self.DF = pms.common.df(pkt['hexStr'])
        self.ICAO = pms.allcall.icao(pkt['hexStr'])
        self.indice = pkt['indice']
        self.squawk = self.callsign = self.altitude = None
        crc = pms.common.crc(pkt['hexStr'])
        if crc <= 31:
            self.crc_ok = True
            self.InterrID = pms.allcall.interrogator(pkt['hexStr'])
        else:
            self.crc_ok = False
            self.InterrID = None

class DF16(ModeSMessage):
    """
    DF16 (Long air-air surveillance / ACAS) message.

    Fields: DF, VS, SL, RI, AC, altitude, address
    """
    def __init__(self, pkt):
        self.DF = pms.common.df(pkt['hexStr'])
        self.ICAO = pms.common.icao(pkt['hexStr'])
        self.indice = pkt['indice']
        self.altitude = pms.common.altcode(pkt['hexStr'])
        self.squawk = self.callsign = None
        self.crc_ok = None

class CommB(ModeSMessage):
    """A message containing a Comm-B reply.

    Fields: MB, callsign
    """

    def __init__(self, pkt):
        self.DF = pms.common.df(pkt['hexStr'])
        self.ICAO = pms.common.icao(pkt['hexStr'])
        self.indice = pkt['indice']
        labels = {
            "BDS10": "Data link capability",
            "BDS17": "GICB capability",
            "BDS20": "Aircraft identification",
            "BDS30": "ACAS resolution",
            "BDS40": "Vertical intention report",
            "BDS50": "Track and turn report",
            "BDS60": "Heading and speed report",
            "BDS44": "Meteorological routine air report",
            "BDS45": "Meteorological hazard report",
            "EMPTY": "[No information available]",
        }

        BDS = pms.bds.infer(pkt['hexStr'], mrar=True)
        if BDS is not None and BDS in labels.keys():
            self.BDS = BDS
            if BDS == "BDS20":
                self.callsign = pms.commb.cs20(pkt['hexStr'])

            if BDS == "BDS40":
                self.MCPalt =  pms.commb.selalt40mcp(pkt['hexStr'])
                self.FMSalt = pms.commb.selalt40fms(pkt['hexStr'])
                self.pressure = pms.commb.p40baro(pkt['hexStr'])

            if BDS == "BDS50":
                self.roll_angle = pms.commb.roll50(pkt['hexStr'])
                self.track_angle = pms.commb.trk50(pkt['hexStr'])
                self.track_rate = pms.commb.rtrk50(pkt['hexStr'])
                self.ground_speed = pms.commb.gs50(pkt['hexStr'])
                self.true_air_speed = pms.commb.tas50(pkt['hexStr'])

            if BDS == "BDS60":
                self.magnetic_heading = pms.commb.hdg60(pkt['hexStr'])
                self.indicated_air_speed = pms.commb.ias60(pkt['hexStr'])
                self.mach_number = pms.commb.mach60(pkt['hexStr'])
                self.vertical_rate_baro = pms.commb.vr60baro(pkt['hexStr'])
                self.vertical_rate_ins = pms.commb.vr60ins(pkt['hexStr'])

            if BDS == "BDS44":
                self.wind_speed = pms.commb.wind44(pkt['hexStr'])[0]
                self.wind_direction = pms.commb.wind44(pkt['hexStr'])[1]
                self.temperature_1 = pms.commb.temp44(pkt['hexStr'])[0]
                self.temperature_2 = pms.commb.temp44(pkt['hexStr'])[1]
                self.pressure = pms.commb.p44(pkt['hexStr'])
                self.humidity = pms.commb.hum44(pkt['hexStr'])
                self.turbulence = pms.commb.turb44(pkt['hexStr'])

            if BDS == "BDS45":
                self.turbulence = pms.commb.turb45(pkt['hexStr'])
                self.wind_shear = pms.commb.ws45(pkt['hexStr'])
                self.microbust = pms.commb.mb45(pkt['hexStr'])
                self.icing = pms.commb.ic45(pkt['hexStr'])
                self.wake_vortex = pms.commb.wv45(pkt['hexStr'])
                self.temperature = pms.commb.temp45(pkt['hexStr'])
                self.pressure = pms.commb.p45(pkt['hexStr'])
                self.radio_height = pms.commb.rh45(pkt['hexStr'])
        else:
            self.BDS = None


class DF20(CommB):
    """
    DF20 (Comm-B, altitude reply) message.

    Fields: DF, FS, DR, UM, AC, altitude, address, MB, callsign
    """

    def __init__(self, pkt):
        CommB.__init__(self, pkt)

        self.DF = pms.common.df(pkt['hexStr'])
        self.ICAO = pms.common.icao(pkt['hexStr'])
        self.indice = pkt['indice']
        self.altitude = pms.common.altcode(pkt['hexStr'])
        self.squawk = None
        self.crc_ok = None

class DF21(CommB):
    """
    DF20 (Comm-B, altitude reply) message.

    Fields: DF, FS, DR, UM, AC, altitude, address, MB, callsign
    """

    def __init__(self, pkt):
        CommB.__init__(self, pkt)
        self.DF = pms.common.df(pkt['hexStr'])
        self.ICAO = pms.common.icao(pkt['hexStr'])
        self.indice = pkt['indice']
        self.squawk = pms.common.idcode(pkt['hexStr'])
        self.altitude = None
        self.crc_ok = None

class DF17(ModeSMessage):
    """DF17 (Extended Squitter) message.

    Fields: DF, CA, AA, address, crc_ok; plus those of ExtendedSquitter.
    """
    def __init__(self, pkt):
        self.DF = pms.common.df(pkt['hexStr'])
        crc = pms.common.crc(pkt['hexStr'])
        if crc == 0:
            self.crc_ok = True
            self.ICAO = pms.adsb.icao(pkt['hexStr'])
            self.indice = pkt['indice']
            tc = pms.adsb.typecode(pkt['hexStr'])
            self.tc = tc
            if tc is None:
                self.callsign = None
            elif 1 <= tc <= 4: #Identification and category
                self.callsign = pms.adsb.callsign(pkt['hexStr'])
            elif 5 <= tc <= 8: # surface position
                self.oe = pms.adsb.oe_flag(pkt['hexStr'])
                msgbin = pms.common.hex2bin(pkt['hexStr'])
                self.cprlat = pms.common.bin2int(msgbin[54:71]) / 131072.0
                self.cprlon = pms.common.bin2int(msgbin[71:88]) / 131072.0
                v = pms.adsb.surface_velocity(pkt['hexStr'])
                self.surface_velocity = v[0]
                self.surface_track = v[1]
            elif 9 <= tc <= 18:  # airborne position
                self.altitude = pms.adsb.altitude(pkt['hexStr'])
                self.oe = pms.adsb.oe_flag(pkt['hexStr'])
                msgbin = pms.common.hex2bin(pkt['hexStr'])
                self.cprlat = pms.common.bin2int(msgbin[54:71]) / 131072.0
                self.cprlon = pms.common.bin2int(msgbin[71:88]) / 131072.0
            elif tc == 19: #airbone velocity
                velocity = pms.adsb.velocity(pkt['hexStr'])
                if velocity is not None:
                    type = velocity[3]
                    if type == "GS":
                        self.ground_speed = velocity[0]
                    elif type == "TAS":
                        self.true_air_speed = velocity[0]
                    else:
                        self.true_air_speed = None
                        self.ground_speed = None
                    self.track = velocity[1]
                    self.vertical_rate_ins = velocity[2] #feet/min
            elif 20 <= tc <= 22:  # airborne position
                self.altitude = pms.adsb.altitude(pkt['hexStr'])
                self.oe = pms.adsb.oe_flag(pkt['hexStr'])
                msgbin = pms.common.hex2bin(pkt['hexStr'])
                self.cprlat = pms.common.bin2int(msgbin[54:71]) / 131072.0
                self.cprlon = pms.common.bin2int(msgbin[71:88]) / 131072.0
            elif tc == 29:  # target state and status
                subtype = pms.common.bin2int((pms.common.hex2bin(pkt['hexStr'])[32:])[5:7])
                if subtype == 0:
                    self.alt, self.alt_source, self.alt_ref = pms.adsb.target_altitude(pkt['hexStr'])
                    self.angle, self.angle_type, self.angle_source = pms.adsb.target_angle(pkt['hexStr'])
                else: #ignore type
                    self.altitude, self.alt_source = pms.adsb.selected_altitude(pkt['hexStr'])
                    self.baro = pms.adsb.baro_pressure_setting(pkt['hexStr'])
                    self.heading = pms.adsb.selected_heading(pkt['hexStr'])
                    self.autopilot = pms.adsb.autopilot(pkt['hexStr'])
                    self.vnav = pms.adsb.vnav_mode(pkt['hexStr'])
                    self.alt_hold = pms.adsb.altitude_hold_mode(pkt['hexStr'])
                    self.app = pms.adsb.approach_mode(pkt['hexStr'])
                    self.lnav = pms.adsb.lnav_mode(pkt['hexStr'])
        else:
            self.crc_ok = False
            self.ICAO = "FFFFFF" # need to work on this later
            self.indice = 999999
            self.tc = 99
message_types = {
    0: DF0,
    4: DF4,
    5: DF5,
    11: DF11,
    16: DF16,
    17: DF17,
    #18: DF18,
    20: DF20,
    21: DF21
}

def decode(pkt):
    """
    Decode a Mode S message.
    Returns a suitable message object, or None if the message type is not
    handled.
    """
    df = pms.common.df(pkt['hexStr'])
    try:
        return message_types[df](pkt)
    except KeyError:
        return None