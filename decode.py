import pyModeS as pms
from prefixes import find_country
def decode(pkt, packet_ID, sdr_id):
    df = pms.common.df(pkt['hexStr'])
    decoded_message = {}
    decoded_message['sdr_id'] = sdr_id
    decoded_message['packetID'] = packet_ID
    decoded_message['df'] = df
    decoded_message['icao'] = pms.common.icao(pkt['hexStr'])
    if decoded_message['icao'] is not None:
        country = find_country(decoded_message['icao'])
        if country is not None:
            decoded_message['country'] = country
        else:
            return None
    else:
        return None
    decoded_message['toa'] = pkt['indice']
    decoded_message['epoch'] = pkt['epoch']
    decoded_message['hexStr'] = pkt['hexStr']
    if df == 0:
        decoded_message['altitude'] = pms.common.altcode(pkt['hexStr'])
        return decoded_message
    elif df == 4:
        decoded_message['altitude'] = pms.common.altcode(pkt['hexStr'])
        return decoded_message
    elif df == 5:
        decoded_message['squawk'] = pms.common.idcode(pkt['hexStr'])
        return decoded_message
    elif df == 11:
        crc = pms.common.crc(pkt['hexStr'])
        if crc <= 31:
            decoded_message['crc_ok'] = True
            decoded_message['InterrID'] = pms.allcall.interrogator(pkt['hexStr'])
        else:
            decoded_message['crc_ok'] = False
            decoded_message['InterrID']  = None
        return decoded_message
    elif df == 16:
        decoded_message['altitude'] = pms.common.altcode(pkt['hexStr'])
        return decoded_message
    elif df == 17:
        crc = pms.common.crc(pkt['hexStr'])
        if crc == 0:
            decoded_message['crc_ok'] = True
            tc = pms.adsb.typecode(pkt['hexStr'])
            if tc is None:
                decoded_message['callsign'] = None
            elif 1 <= tc <= 4:  # Identification and category
                decoded_message['callsign'] = pms.adsb.callsign(pkt['hexStr'])
            elif 5 <= tc <= 8:  # surface position
                decoded_message['oe'] = pms.adsb.oe_flag(pkt['hexStr'])
                msgbin = pms.common.hex2bin(pkt['hexStr'])
                decoded_message['cprlat'] = pms.common.bin2int(msgbin[54:71]) / 131072.0
                decoded_message['cprlon'] = pms.common.bin2int(msgbin[71:88]) / 131072.0
                v = pms.adsb.surface_velocity(pkt['hexStr'])
                if v is not None:
                    decoded_message['velocity'] = int(v[0])
                    decoded_message['track'] = v[1]
            elif 9 <= tc <= 18:  # airborne position
                decoded_message['altitude'] = pms.adsb.altitude(pkt['hexStr'])
                decoded_message['oe'] = pms.adsb.oe_flag(pkt['hexStr'])
                msgbin = pms.common.hex2bin(pkt['hexStr'])
                decoded_message['cprlat'] = pms.common.bin2int(msgbin[54:71]) / 131072.0
                decoded_message['cprlon'] = pms.common.bin2int(msgbin[71:88]) / 131072.0
            elif tc == 19:  # airbone velocity
                velocity = pms.adsb.velocity(pkt['hexStr'])
                if velocity is not None:
                    type = velocity[3]
                    if type == "GS":
                        decoded_message['velocity'] = int(velocity[0])
                    elif type == "TAS":
                        decoded_message['velocity'] = int(velocity[0])
                    else:
                        decoded_message['velocity'] = None
                    decoded_message['track'] = velocity[1]
                    decoded_message['ver_rate'] = velocity[2]  # feet/min
            elif 20 <= tc <= 22:  # airborne position
                decoded_message['altitude'] = pms.adsb.altitude(pkt['hexStr'])
                decoded_message['oe'] = pms.adsb.oe_flag(pkt['hexStr'])
                msgbin = pms.common.hex2bin(pkt['hexStr'])
                decoded_message['cprlat'] = pms.common.bin2int(msgbin[54:71]) / 131072.0
                decoded_message['cprlon'] = pms.common.bin2int(msgbin[71:88]) / 131072.0
            elif tc == 29:  # target state and status
                subtype = pms.common.bin2int((pms.common.hex2bin(pkt['hexStr'])[32:])[5:7])
                if subtype == 0:
                    decoded_message['altitude'] = pms.adsb.target_altitude(pkt['hexStr'])[0]
                    decoded_message['angle'] = pms.adsb.target_angle(pkt['hexStr'])[0]
                else:  # ignore type
                    decoded_message['altitude'] = pms.adsb.selected_altitude(pkt['hexStr'])[0]
                    decoded_message['heading'] = pms.adsb.selected_heading(pkt['hexStr'])
            return decoded_message
        else: #CRC False
            return None
    elif df == 20 or df == 21:
        if df == 20:
            decoded_message['altitude'] = pms.common.altcode(pkt['hexStr'])
        else:
            decoded_message['squawk'] = pms.common.idcode(pkt['hexStr'])
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
            if BDS == "BDS20":
                decoded_message['callsign'] = pms.commb.cs20(pkt['hexStr'])
            if BDS == "BDS40":
                decoded_message['altitude'] = pms.commb.selalt40fms(pkt['hexStr'])
            if BDS == "BDS50":
                decoded_message['track'] = pms.commb.trk50(pkt['hexStr'])
                decoded_message['velocity'] = int(pms.commb.tas50(pkt['hexStr']))
            if BDS == "BDS60":
                decoded_message['ver_rate'] = pms.commb.vr60ins(pkt['hexStr'])
        return decoded_message
    else:
        return None