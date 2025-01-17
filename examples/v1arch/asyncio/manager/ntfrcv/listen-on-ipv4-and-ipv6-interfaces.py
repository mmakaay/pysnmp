"""
Listen for notifications at IPv4 & IPv6 interfaces
++++++++++++++++++++++++++++++++++++++++++++++++++

Receive SNMP TRAP messages with the following options:

* SNMPv1/SNMPv2c
* with SNMP community "public"
* over IPv4/UDP, listening at 127.0.0.1:162
* over IPv6/UDP, listening at [::1]:162
* print received data on stdout

Either of the following Net-SNMP commands will send notifications to this
receiver:

| $ snmptrap -v1 -c public 127.0.0.1 1.3.6.1.4.1.20408.4.1.1.2 127.0.0.1 1 1 123 1.3.6.1.2.1.1.1.0 s test
| $ snmptrap -v2c -c public ::1 123 1.3.6.1.6.3.1.1.5.1 1.3.6.1.2.1.1.5.0 s test

Notification Receiver below uses two different transports for communication
with Notification Originators - UDP over IPv4 and UDP over IPv6.

"""  #
from pysnmp.carrier.asyncio.dispatch import AsyncioDispatcher
from pysnmp.carrier.asyncio.dgram import udp, udp6
from pyasn1.codec.ber import decoder
from pysnmp.proto import api


# noinspection PyUnusedLocal
def cbFun(transportDispatcher, transportDomain, transportAddress, wholeMsg):
    while wholeMsg:
        msgVer = int(api.decodeMessageVersion(wholeMsg))
        if msgVer in api.PROTOCOL_MODULES:
            pMod = api.PROTOCOL_MODULES[msgVer]

        else:
            print("Unsupported SNMP version %s" % msgVer)
            return

        reqMsg, wholeMsg = decoder.decode(
            wholeMsg,
            asn1Spec=pMod.Message(),
        )

        print(
            "Notification message from {}:{}: ".format(
                transportDomain, transportAddress
            )
        )

        reqPDU = pMod.apiMessage.getPDU(reqMsg)
        if reqPDU.isSameTypeWith(pMod.TrapPDU()):
            if msgVer == api.SNMP_VERSION_1:
                print(
                    "Enterprise: %s"
                    % (pMod.apiTrapPDU.getEnterprise(reqPDU).prettyPrint())
                )
                print(
                    "Agent Address: %s"
                    % (pMod.apiTrapPDU.getAgentAddr(reqPDU).prettyPrint())
                )
                print(
                    "Generic Trap: %s"
                    % (pMod.apiTrapPDU.getGenericTrap(reqPDU).prettyPrint())
                )
                print(
                    "Specific Trap: %s"
                    % (pMod.apiTrapPDU.getSpecificTrap(reqPDU).prettyPrint())
                )
                print(
                    "Uptime: %s" % (pMod.apiTrapPDU.getTimeStamp(reqPDU).prettyPrint())
                )
                varBinds = pMod.apiTrapPDU.getVarBinds(reqPDU)

            else:
                varBinds = pMod.apiPDU.getVarBinds(reqPDU)

            print("Var-binds:")

            for oid, val in varBinds:
                print(f"{oid.prettyPrint()} = {val.prettyPrint()}")

    return wholeMsg


transportDispatcher = AsyncioDispatcher()

transportDispatcher.registerRecvCbFun(cbFun)

# UDP/IPv4
transportDispatcher.registerTransport(
    udp.DOMAIN_NAME, udp.UdpAsyncioTransport().openServerMode(("localhost", 162))
)

# UDP/IPv6
transportDispatcher.registerTransport(
    udp6.DOMAIN_NAME, udp6.Udp6AsyncioTransport().openServerMode(("::1", 162))
)

transportDispatcher.jobStarted(1)

try:
    # Dispatcher will never finish as job#1 never reaches zero
    transportDispatcher.runDispatcher()

finally:
    transportDispatcher.closeDispatcher()
