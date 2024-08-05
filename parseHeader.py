def parseHeader(rawBits):
    downlinkFormat = sum([16, 8, 4, 2, 1] * rawBits[0:5])
    capability = sum([4, 2, 1] * rawBits[5:8])
    return downlinkFormat,capability

