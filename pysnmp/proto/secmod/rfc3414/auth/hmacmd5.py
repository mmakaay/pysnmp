#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from hashlib import md5
from pyasn1.type import univ
from pysnmp.proto.secmod.rfc3414.auth import base
from pysnmp.proto.secmod.rfc3414 import localkey
from pysnmp.proto import errind, error

TWELVE_ZEROS = univ.OctetString((0,) * 12).asOctets()
FORTY_EIGHT_ZEROS = (0,) * 48


# rfc3414: 6.2.4


class HmacMd5(base.AbstractAuthenticationService):
    SERVICE_ID = (1, 3, 6, 1, 6, 3, 10, 1, 1, 2)  # usmHMACMD5AuthProtocol
    IPAD = [0x36] * 64
    OPAD = [0x5C] * 64

    def hashPassphrase(self, authKey):
        return localkey.hashPassphraseMD5(authKey)

    def localizeKey(self, authKey, snmpEngineID):
        return localkey.localizeKeyMD5(authKey, snmpEngineID)

    @property
    def digestLength(self):
        return 12

    # 6.3.1
    def authenticateOutgoingMsg(self, authKey, wholeMsg):
        # Here we expect calling secmod to indicate where the digest
        # should be in the substrate. Also, it pre-sets digest placeholder
        # so we hash wholeMsg out of the box.
        # Yes, that's ugly but that's rfc...
        l = wholeMsg.find(TWELVE_ZEROS)
        if l == -1:
            raise error.ProtocolError("Cant locate digest placeholder")
        wholeHead = wholeMsg[:l]
        wholeTail = wholeMsg[l + 12 :]

        # 6.3.1.1

        # 6.3.1.2a
        extendedAuthKey = authKey.asNumbers() + FORTY_EIGHT_ZEROS

        # 6.3.1.2b --> no-op

        # 6.3.1.2c
        k1 = univ.OctetString(map(lambda x, y: x ^ y, extendedAuthKey, self.IPAD))

        # 6.3.1.2d --> no-op

        # 6.3.1.2e
        k2 = univ.OctetString(map(lambda x, y: x ^ y, extendedAuthKey, self.OPAD))

        # 6.3.1.3
        # noinspection PyDeprecation,PyCallingNonCallable
        d1 = md5(k1.asOctets() + wholeMsg).digest()

        # 6.3.1.4
        # noinspection PyDeprecation,PyCallingNonCallable
        d2 = md5(k2.asOctets() + d1).digest()
        mac = d2[:12]

        # 6.3.1.5 & 6
        return wholeHead + mac + wholeTail

    # 6.3.2
    def authenticateIncomingMsg(self, authKey, authParameters, wholeMsg):
        # 6.3.2.1 & 2
        if len(authParameters) != 12:
            raise error.StatusInformation(errorIndication=errind.authenticationError)

        # 6.3.2.3
        l = wholeMsg.find(authParameters.asOctets())
        if l == -1:
            raise error.ProtocolError("Cant locate digest in wholeMsg")
        wholeHead = wholeMsg[:l]
        wholeTail = wholeMsg[l + 12 :]
        authenticatedWholeMsg = wholeHead + TWELVE_ZEROS + wholeTail

        # 6.3.2.4a
        extendedAuthKey = authKey.asNumbers() + FORTY_EIGHT_ZEROS

        # 6.3.2.4b --> no-op

        # 6.3.2.4c
        k1 = univ.OctetString(map(lambda x, y: x ^ y, extendedAuthKey, self.IPAD))

        # 6.3.2.4d --> no-op

        # 6.3.2.4e
        k2 = univ.OctetString(map(lambda x, y: x ^ y, extendedAuthKey, self.OPAD))

        # 6.3.2.5a
        # noinspection PyDeprecation,PyCallingNonCallable
        d1 = md5(k1.asOctets() + authenticatedWholeMsg).digest()

        # 6.3.2.5b
        # noinspection PyDeprecation,PyCallingNonCallable
        d2 = md5(k2.asOctets() + d1).digest()

        # 6.3.2.5c
        mac = d2[:12]

        # 6.3.2.6
        if mac != authParameters:
            raise error.StatusInformation(errorIndication=errind.authenticationFailure)

        return authenticatedWholeMsg
