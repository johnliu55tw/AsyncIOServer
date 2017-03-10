#!/usr/bin/env python3

import argparse
import selectors
import socket
import ssl


def createServerSocket(host, port, listenNumber=100):
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSock.bind((host, port))
    serverSock.listen(listenNumber)
    serverSock.setblocking(False)
    return serverSock


def clientRead(selectorObj, clientSock, mask):
    try:
        data = clientSock.recv(1000)  # Should be ready
        if not data:
            raise EOFError("No data received.")
        else:
            print("Data received from {}: {}".format(
                clientSock.getsockname(), data))
            clientSock.send(b"\xFF\x01\x00\x00\xFF\x01\x00\x00")
    except Exception as e:
        print('{}: Error: {}. Closing.'.format(
            clientSock.getsockname(), repr(e)))
        selectorObj.unregister(clientSock)
        clientSock.close()


def acceptClientSocket(selectorObj, serverSock, mask):
    clientSock, addr = serverSock.accept()  # Should be ready
    print('Port {}: Accepted regular connection from: {}'.format(
        serverSock.getsockname()[1], addr))
    clientSock.setblocking(False)
    selectorObj.register(clientSock, selectors.EVENT_READ, clientRead)


if __name__ == "__main__":
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

    sel = selectors.DefaultSelector()
    # Register server socket
    if args.ssl is True:
        print("Waiting for SSL connection on {}:{}".format(
            args.host, args.port))
        serverSock = ssl.wrap_socket(
                sock=createServerSocket(args.host, args.port, args.listen),
                keyfile=args.key,
                certfile=args.cert,
                server_side=True)
    else:
        print("Waiting for unencrypted TCP connection on {}:{}".format(
            args.host, args.port))
        serverSock = createServerSocket(args.host, args.port, args.listen)

    sel.register(serverSock,
                 selectors.EVENT_READ,
                 acceptClientSocket)

    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(sel, key.fileobj, mask)
