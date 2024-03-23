#
# This file is part of pysnmp software.
#
# Copyright (c) 2005-2020, Ilya Etingof <etingof@gmail.com>
# License: http://www.pysnmp.com/pysnmp/license.html
#
# ASN.1 source http://mibs.pysnmp.com:80/asn1/SNMPv2-TM
# Produced by pysmi-0.4.0 at Sun Feb 17 08:56:38 2019
#
# Parts of otherwise autogenerated MIB has been updated manually.
#

try:
    from socket import inet_ntop, inet_pton, AF_INET

except ImportError:
    from socket import inet_ntoa, inet_aton, AF_INET

    inet_ntop = lambda x, y: inet_ntoa(y)
    inet_pton = lambda x, y: inet_aton(y)

from pyasn1.compat.octets import int2oct
from pyasn1.compat.octets import oct2int

if "mibBuilder" not in globals():
    import sys

    sys.stderr.write(__doc__)
    sys.exit(1)

(Integer, OctetString, ObjectIdentifier) = mibBuilder.importSymbols(
    "ASN1", "Integer", "OctetString", "ObjectIdentifier"
)

(NamedValues,) = mibBuilder.importSymbols("ASN1-ENUMERATION", "NamedValues")

(
    ConstraintsIntersection,
    SingleValueConstraint,
    ValueRangeConstraint,
    ValueSizeConstraint,
    ConstraintsUnion,
) = mibBuilder.importSymbols(
    "ASN1-REFINEMENT",
    "ConstraintsIntersection",
    "SingleValueConstraint",
    "ValueRangeConstraint",
    "ValueSizeConstraint",
    "ConstraintsUnion",
)


(
    Counter64,
    iso,
    NotificationType,
    ObjectIdentity,
    Bits,
    ModuleIdentity,
    TimeTicks,
    Counter32,
    IpAddress,
    snmpProxys,
    MibScalar,
    MibTable,
    MibTableRow,
    MibTableColumn,
    Gauge32,
    Unsigned32,
    snmpDomains,
    Integer32,
    MibIdentifier,
    snmpModules,
) = mibBuilder.importSymbols(
    "SNMPv2-SMI",
    "Counter64",
    "iso",
    "NotificationType",
    "ObjectIdentity",
    "Bits",
    "ModuleIdentity",
    "TimeTicks",
    "Counter32",
    "IpAddress",
    "snmpProxys",
    "MibScalar",
    "MibTable",
    "MibTableRow",
    "MibTableColumn",
    "Gauge32",
    "Unsigned32",
    "snmpDomains",
    "Integer32",
    "MibIdentifier",
    "snmpModules",
)

(TextualConvention,) = mibBuilder.importSymbols("SNMPv2-TC", "TextualConvention")

snmpv2tm = ModuleIdentity((1, 3, 6, 1, 6, 3, 19))
snmpv2tm.setRevisions(("2002-10-16 00:00", "1996-01-01 00:00", "1993-04-01 00:00"))
snmpv2tm.setLastUpdated("200210160000Z")
if mibBuilder.loadTexts:
    snmpv2tm.setOrganization(
        """\
IETF SNMPv3 Working Group
"""
    )
snmpv2tm.setContactInfo(
    """\
WG-EMail: snmpv3@lists.tislabs.com Subscribe: snmpv3-request@lists.tislabs.com
Co-Chair: Russ Mundy Network Associates Laboratories postal: 15204 Omega Drive,
Suite 300 Rockville, MD 20850-4601 USA EMail: mundy@tislabs.com phone: +1 301
947-7107 Co-Chair: David Harrington Enterasys Networks postal: 35 Industrial
Way P. O. Box 5005 Rochester, NH 03866-5005 USA EMail: dbh@enterasys.com phone:
+1 603 337-2614 Editor: Randy Presuhn BMC Software, Inc. postal: 2141 North
First Street San Jose, CA 95131 USA EMail: randy_presuhn@bmc.com phone: +1 408
546-1006
"""
)
if mibBuilder.loadTexts:
    snmpv2tm.setDescription(
        """\
The MIB module for SNMP transport mappings. Copyright (C) The Internet Society
(2002). This version of this MIB module is part of RFC 3417; see the RFC itself
for full legal notices.
"""
    )


class SnmpUDPAddress(TextualConvention, OctetString):
    status = "current"
    displayHint = "1d.1d.1d.1d/2d"
    subtypeSpec = OctetString.subtypeSpec
    subtypeSpec += ConstraintsUnion(
        ValueSizeConstraint(6, 6),
    )

    if mibBuilder.loadTexts:
        description = """\
Represents a UDP over IPv4 address: octets contents encoding 1-4 IP-address
network-byte order 5-6 UDP-port network-byte order
"""
    fixedLength = 6

    def prettyIn(self, value):
        if isinstance(value, tuple):
            # Wild hack -- need to implement TextualConvention.prettyIn
            value = (
                inet_pton(AF_INET, value[0])
                + int2oct((value[1] >> 8) & 0xFF)
                + int2oct(value[1] & 0xFF)
            )
        return OctetString.prettyIn(self, value)

    # Socket address syntax coercion
    def __asSocketAddress(self):
        if not hasattr(self, "__tuple_value"):
            v = self.asOctets()
            self.__tuple_value = (
                inet_ntop(AF_INET, v[:4]),
                oct2int(v[4]) << 8 | oct2int(v[5]),
            )
        return self.__tuple_value

    def __iter__(self):
        return iter(self.__asSocketAddress())

    def __getitem__(self, item):
        return self.__asSocketAddress()[item]


class SnmpOSIAddress(TextualConvention, OctetString):
    status = "current"
    displayHint = "*1x:/1x:"
    subtypeSpec = OctetString.subtypeSpec
    subtypeSpec += ConstraintsUnion(
        ValueSizeConstraint(1, 1),
        ValueSizeConstraint(4, 85),
    )

    if mibBuilder.loadTexts:
        description = """\
Represents an OSI transport-address: octets contents encoding 1 length of NSAP
'n' as an unsigned-integer (either 0 or from 3 to 20) 2..(n+1) NSAP concrete
binary representation (n+2)..m TSEL string of (up to 64) octets
"""


class SnmpNBPAddress(TextualConvention, OctetString):
    status = "current"
    subtypeSpec = OctetString.subtypeSpec
    subtypeSpec += ConstraintsUnion(
        ValueSizeConstraint(3, 99),
    )

    if mibBuilder.loadTexts:
        description = """\
Represents an NBP name: octets contents encoding 1 length of object 'n' as an
unsigned integer 2..(n+1) object string of (up to 32) octets n+2 length of type
'p' as an unsigned integer (n+3)..(n+2+p) type string of (up to 32) octets
n+3+p length of zone 'q' as an unsigned integer (n+4+p)..(n+3+p+q) zone string
of (up to 32) octets For comparison purposes, strings are case-insensitive. All
strings may contain any octet other than 255 (hex ff).
"""


class SnmpIPXAddress(TextualConvention, OctetString):
    status = "current"
    displayHint = "4x.1x:1x:1x:1x:1x:1x.2d"
    subtypeSpec = OctetString.subtypeSpec
    subtypeSpec += ConstraintsUnion(
        ValueSizeConstraint(12, 12),
    )

    if mibBuilder.loadTexts:
        description = """\
Represents an IPX address: octets contents encoding 1-4 network-number network-
byte order 5-10 physical-address network-byte order 11-12 socket-number
network-byte order
"""
    fixedLength = 12


_SnmpUDPDomain_ObjectIdentity = ObjectIdentity
snmpUDPDomain = _SnmpUDPDomain_ObjectIdentity((1, 3, 6, 1, 6, 1, 1))
if mibBuilder.loadTexts:
    snmpUDPDomain.setStatus("current")
if mibBuilder.loadTexts:
    snmpUDPDomain.setDescription(
        """\
The SNMP over UDP over IPv4 transport domain. The corresponding transport
address is of type SnmpUDPAddress.
"""
    )
_SnmpCLNSDomain_ObjectIdentity = ObjectIdentity
snmpCLNSDomain = _SnmpCLNSDomain_ObjectIdentity((1, 3, 6, 1, 6, 1, 2))
if mibBuilder.loadTexts:
    snmpCLNSDomain.setStatus("current")
if mibBuilder.loadTexts:
    snmpCLNSDomain.setDescription(
        """\
The SNMP over CLNS transport domain. The corresponding transport address is of
type SnmpOSIAddress.
"""
    )
_SnmpCONSDomain_ObjectIdentity = ObjectIdentity
snmpCONSDomain = _SnmpCONSDomain_ObjectIdentity((1, 3, 6, 1, 6, 1, 3))
if mibBuilder.loadTexts:
    snmpCONSDomain.setStatus("current")
if mibBuilder.loadTexts:
    snmpCONSDomain.setDescription(
        """\
The SNMP over CONS transport domain. The corresponding transport address is of
type SnmpOSIAddress.
"""
    )
_SnmpDDPDomain_ObjectIdentity = ObjectIdentity
snmpDDPDomain = _SnmpDDPDomain_ObjectIdentity((1, 3, 6, 1, 6, 1, 4))
if mibBuilder.loadTexts:
    snmpDDPDomain.setStatus("current")
if mibBuilder.loadTexts:
    snmpDDPDomain.setDescription(
        """\
The SNMP over DDP transport domain. The corresponding transport address is of
type SnmpNBPAddress.
"""
    )
_SnmpIPXDomain_ObjectIdentity = ObjectIdentity
snmpIPXDomain = _SnmpIPXDomain_ObjectIdentity((1, 3, 6, 1, 6, 1, 5))
if mibBuilder.loadTexts:
    snmpIPXDomain.setStatus("current")
if mibBuilder.loadTexts:
    snmpIPXDomain.setDescription(
        """\
The SNMP over IPX transport domain. The corresponding transport address is of
type SnmpIPXAddress.
"""
    )
_Rfc1157Proxy_ObjectIdentity = ObjectIdentity
rfc1157Proxy = _Rfc1157Proxy_ObjectIdentity((1, 3, 6, 1, 6, 2, 1))
_Rfc1157Domain_ObjectIdentity = ObjectIdentity
rfc1157Domain = _Rfc1157Domain_ObjectIdentity((1, 3, 6, 1, 6, 2, 1, 1))
if mibBuilder.loadTexts:
    rfc1157Domain.setStatus("deprecated")
if mibBuilder.loadTexts:
    rfc1157Domain.setDescription(
        """\
The transport domain for SNMPv1 over UDP over IPv4. The corresponding transport
address is of type SnmpUDPAddress.
"""
    )

mibBuilder.exportSymbols(
    "SNMPv2-TM",
    **{
        "SnmpUDPAddress": SnmpUDPAddress,
        "SnmpOSIAddress": SnmpOSIAddress,
        "SnmpNBPAddress": SnmpNBPAddress,
        "SnmpIPXAddress": SnmpIPXAddress,
        "snmpUDPDomain": snmpUDPDomain,
        "snmpCLNSDomain": snmpCLNSDomain,
        "snmpCONSDomain": snmpCONSDomain,
        "snmpDDPDomain": snmpDDPDomain,
        "snmpIPXDomain": snmpIPXDomain,
        "rfc1157Proxy": rfc1157Proxy,
        "rfc1157Domain": rfc1157Domain,
        "snmpv2tm": snmpv2tm,
    }
)
