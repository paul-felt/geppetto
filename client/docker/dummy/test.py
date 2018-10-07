from autobahn.asyncio.component import Component
from autobahn.asyncio.component import run

component = Component(
    transports=u"ws://plfelt-mbp.local:8081/ws",
    realm=u"realm1",
)

@component.on_join
async def join(session, details):
    print("joined {}: {}".format(session, details))

run([component])
