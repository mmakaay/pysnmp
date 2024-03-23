#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: https://www.pysnmp.com/pysnmp/license.html
#
from pysnmp import nextid
from pysnmp.proto import error


class Cache:
    __stateReference = nextid.Integer(0xFFFFFF)

    def __init__(self):
        self.__cacheEntries = {}

    def push(self, **securityData):
        stateReference = self.__stateReference()
        self.__cacheEntries[stateReference] = securityData
        return stateReference

    def pop(self, stateReference):
        if stateReference in self.__cacheEntries:
            return self.__cacheEntries.pop(stateReference)

        raise error.ProtocolError(
            "Cache miss for stateReference=%s at " "%s" % (stateReference, self)
        )
