"""
SET string and integer scalars (SNMPv2c)
++++++++++++++++++++++++++++++++++++++++

Perform SNMP SET operation with the following options:

* with SNMPv2c, community 'public'
* over IPv4/UDP
* to an Agent at demo.pysnmp.com:161
* for OIDs in string form and values in form of pyasn1 objects

This script performs similar to the following Net-SNMP command:

| $ snmpset -v2c -c public -ObentU demo.pysnmp.com 1.3.6.1.2.1.1.9.1.3.1 s 'New description' 1.3.6.1.2.1.1.9.1.4.1 t 12

"""  #
from pysnmp.carrier.asyncio.dispatch import AsyncioDispatcher
from pysnmp.carrier.asyncio.dgram import udp
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto import api
from time import time

# Protocol version to use
# pMod = api.protoModules[api.protoVersion1]
pMod = api.PROTOCOL_MODULES[api.SNMP_VERSION_1]

# Build PDU
reqPDU = pMod.SetRequestPDU()
pMod.apiPDU.setDefaults(reqPDU)
pMod.apiPDU.setVarBinds(
    reqPDU,
    # A list of Var-Binds to SET
    (
        ("1.3.6.1.2.1.1.9.1.3.1", pMod.OctetString("New system description")),
        ("1.3.6.1.2.1.1.9.1.4.1", pMod.TimeTicks(12)),
    ),
)

# Build message
reqMsg = pMod.Message()
pMod.apiMessage.setDefaults(reqMsg)
pMod.apiMessage.setCommunity(reqMsg, "public")
pMod.apiMessage.setPDU(reqMsg, reqPDU)


# noinspection PyUnusedLocal,PyUnusedLocal
def cbRecvFun(
    transportDispatcher, transportDomain, transportAddress, wholeMsg, reqPDU=reqPDU
):
    while wholeMsg:
        rspMsg, wholeMsg = decoder.decode(wholeMsg, asn1Spec=pMod.Message())
        rspPDU = pMod.apiMessage.getPDU(rspMsg)

        # Match response to request
        if pMod.apiPDU.getRequestID(reqPDU) == pMod.apiPDU.getRequestID(rspPDU):
            # Check for SNMP errors reported
            errorStatus = pMod.apiPDU.getErrorStatus(rspPDU)
            if errorStatus:
                print(errorStatus.prettyPrint())

            else:
                for oid, val in pMod.apiPDU.getVarBinds(rspPDU):
                    print(f"{oid.prettyPrint()} = {val.prettyPrint()}")

            transportDispatcher.jobFinished(1)

    return wholeMsg


transportDispatcher = AsyncioDispatcher()

transportDispatcher.registerRecvCbFun(cbRecvFun)

# UDP/IPv4
transportDispatcher.registerTransport(
    udp.DOMAIN_NAME, udp.UdpAsyncioTransport().openClientMode()
)

# Pass message to dispatcher
transportDispatcher.sendMessage(
    encoder.encode(reqMsg), udp.DOMAIN_NAME, ("demo.pysnmp.com", 161)
)

transportDispatcher.jobStarted(1)

# Dispatcher will finish as job#1 counter reaches zero
transportDispatcher.runDispatcher(3)

transportDispatcher.closeDispatcher()
