#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from hashlib import md5, sha1
import random

try:
    from pysnmpcrypto import des, PysnmpCryptoError

except ImportError:
    PysnmpCryptoError = AttributeError
    des = None

from pysnmp.proto.secmod.rfc3414.priv import base
from pysnmp.proto.secmod.rfc3414.auth import hmacmd5, hmacsha
from pysnmp.proto.secmod.rfc3414 import localkey
from pysnmp.proto.secmod.rfc7860.auth import hmacsha2
from pysnmp.proto import errind, error
from pyasn1.type import univ

random.seed()


# 8.2.4


class Des(base.AbstractEncryptionService):
    SERVICE_ID = (1, 3, 6, 1, 6, 3, 10, 1, 2, 2)  # usmDESPrivProtocol
    KEY_SIZE = 16

    local_int = random.randrange(0, 0xFFFFFFFF)

    def hashPassphrase(self, authProtocol, privKey):
        if authProtocol == hmacmd5.HmacMd5.SERVICE_ID:
            hashAlgo = md5
        elif authProtocol == hmacsha.HmacSha.SERVICE_ID:
            hashAlgo = sha1
        elif authProtocol in hmacsha2.HmacSha2.HASH_ALGORITHM:
            hashAlgo = hmacsha2.HmacSha2.HASH_ALGORITHM[authProtocol]
        else:
            raise error.ProtocolError(f"Unknown auth protocol {authProtocol}")
        return localkey.hashPassphrase(privKey, hashAlgo)

    def localizeKey(self, authProtocol, privKey, snmpEngineID):
        if authProtocol == hmacmd5.HmacMd5.SERVICE_ID:
            hashAlgo = md5
        elif authProtocol == hmacsha.HmacSha.SERVICE_ID:
            hashAlgo = sha1
        elif authProtocol in hmacsha2.HmacSha2.HASH_ALGORITHM:
            hashAlgo = hmacsha2.HmacSha2.HASH_ALGORITHM[authProtocol]
        else:
            raise error.ProtocolError(f"Unknown auth protocol {authProtocol}")
        localPrivKey = localkey.localizeKey(privKey, snmpEngineID, hashAlgo)
        return localPrivKey[: self.KEY_SIZE]

    # 8.1.1.1
    def __getEncryptionKey(self, privKey, snmpEngineBoots):
        desKey = privKey[:8]
        preIV = privKey[8:16]

        securityEngineBoots = int(snmpEngineBoots)

        salt = [
            securityEngineBoots >> 24 & 0xFF,
            securityEngineBoots >> 16 & 0xFF,
            securityEngineBoots >> 8 & 0xFF,
            securityEngineBoots & 0xFF,
            self.local_int >> 24 & 0xFF,
            self.local_int >> 16 & 0xFF,
            self.local_int >> 8 & 0xFF,
            self.local_int & 0xFF,
        ]
        if self.local_int == 0xFFFFFFFF:
            self.local_int = 0
        else:
            self.local_int += 1

        return (
            desKey.asOctets(),
            univ.OctetString(salt).asOctets(),
            univ.OctetString(
                map(lambda x, y: x ^ y, salt, preIV.asNumbers())
            ).asOctets(),
        )

    @staticmethod
    def __getDecryptionKey(privKey, salt):
        return (
            privKey[:8].asOctets(),
            univ.OctetString(
                map(lambda x, y: x ^ y, salt.asNumbers(), privKey[8:16].asNumbers())
            ).asOctets(),
        )

    # 8.2.4.1
    def encryptData(self, encryptKey, privParameters, dataToEncrypt):
        if des is None:
            raise error.StatusInformation(errorIndication=errind.encryptionError)

        snmpEngineBoots, snmpEngineTime, salt = privParameters

        # 8.3.1.1
        desKey, salt, iv = self.__getEncryptionKey(encryptKey, snmpEngineBoots)

        # 8.3.1.2
        privParameters = univ.OctetString(salt)

        # 8.1.1.2
        plaintext = (
            dataToEncrypt
            + univ.OctetString((0,) * (8 - len(dataToEncrypt) % 8)).asOctets()
        )

        try:
            ciphertext = des.encrypt(plaintext, desKey, iv)

        except PysnmpCryptoError:
            raise error.StatusInformation(
                errorIndication=errind.unsupportedPrivProtocol
            )

        # 8.3.1.3 & 4
        return univ.OctetString(ciphertext), privParameters

    # 8.2.4.2
    def decryptData(self, decryptKey, privParameters, encryptedData):
        if des is None:
            raise error.StatusInformation(errorIndication=errind.decryptionError)

        snmpEngineBoots, snmpEngineTime, salt = privParameters

        # 8.3.2.1
        if len(salt) != 8:
            raise error.StatusInformation(errorIndication=errind.decryptionError)

        # 8.3.2.2 no-op

        # 8.3.2.3
        desKey, iv = self.__getDecryptionKey(decryptKey, salt)

        # 8.3.2.4 -> 8.1.1.3
        if len(encryptedData) % 8 != 0:
            raise error.StatusInformation(errorIndication=errind.decryptionError)

        try:
            # 8.3.2.6
            return des.decrypt(encryptedData.asOctets(), desKey, iv)

        except PysnmpCryptoError:
            raise error.StatusInformation(
                errorIndication=errind.unsupportedPrivProtocol
            )
