#!/usr/bin/env python3
import sys
import argparse
import ssl
import asyncio
import show_data


class EchoServerClientProtocol(asyncio.Protocol):

    def __init__(self):
        self.transport = None
        self.peername = None
        self.displayer = None
        self.buffer = b""

    def connection_made(self, transport):
        self.peername = transport.get_extra_info('peername')
        self.transport = transport
        self.displayer = show_data.Displayer(
                stream=sys.stdout,
                name="{}:{}".format(self.peername[0], self.peername[1]))
        print('Accepted connection from {}'.format(self.peername))

    def data_received(self, data):
        self.displayer.show(data)
        self.transport.write(b"\xFF\x01\x00\x00\xFF\x01\x00\x00")

    def connection_lost(self, exc):
        print("Lost connection from: {}".format(
            self.peername, exc))
        self.transport.close()


if __name__ == "__main__":
    # Parsing arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default="0.0.0.0",
                        help="The host to listen on. Default to 0.0.0.0")
    parser.add_argument('--port', type=int, default=9001,
                        help="The port number. Default to 9001")
    parser.add_argument('--listen', type=int, default=10,
                        help="The listen number. Default to 10.")
    parser.add_argument('--ssl', action='store_true', default=False,
                        help="Enable SSL/TLS. Disabled by default.")
    parser.add_argument('--cert', type=str,
                        help="The path of the certificate *.crt file.")
    parser.add_argument('--key', type=str,
                        help="The path of the private key *.key file.")
    args = parser.parse_args()

    # Create server event loop
    loop = asyncio.get_event_loop()
    if args.ssl is True:
        sslCtx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        sslCtx.load_cert_chain(certfile=args.cert,
                               keyfile=args.key)
        coro = loop.create_server(EchoServerClientProtocol,
                                  args.host, args.port,
                                  ssl=sslCtx)
    else:
        coro = loop.create_server(EchoServerClientProtocol,
                                  args.host, args.port)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
