#!/usr/bin/env python3
import asyncio

import autobahn.asyncio.wamp
import autobahn.asyncio.websocket
import autobahn.wamp.router


class MyBackendComponent(autobahn.asyncio.wamp.ApplicationSession):
    def onConnect(self):
        self.join(u"org.srobo")

    @asyncio.coroutine
    def onJoin(self, details):
        counter = 1.0
        while True:
            self.publish("org.srobo.battery.level", counter)
            counter -= 0.01
            yield from asyncio.sleep(1)


if __name__ == "__main__":
    router_factory = autobahn.wamp.router.RouterFactory()
    session_factory = autobahn.asyncio.wamp.RouterSessionFactory(router_factory)
    session_factory.add(MyBackendComponent())
    transport_factory = autobahn.asyncio.websocket.WampWebSocketServerFactory(session_factory,
                                                                              debug=True,
                                                                              debug_wamp=True)

    loop = asyncio.get_event_loop()
    coro = loop.create_server(transport_factory, "0.0.0.0", 8080)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
