#!/usr/bin/env python3

import selectors
import socket
import ssl


CERT_FILE = "/home/john/SslCert/server.crt"
KEY_FILE = "/home/john/SslCert/server.key"


def createServerSocket(addressTuple, listenNumber=100):
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSock.bind(addressTuple)
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
    print('Accepted regular connection from: {}'.format(addr))
    clientSock.setblocking(False)
    selectorObj.register(clientSock, selectors.EVENT_READ, clientRead)


def acceptSslClientSocket(selectorObj, serverSock, mask):
    # Create SSL context
    sslCtx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    sslCtx.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

    clientSock, addr = serverSock.accept()  # Should be ready
    print('Accepted SSL connection from: {}'.format(addr))
    clientSock = sslCtx.wrap_socket(clientSock, server_side=True)
    clientSock.setblocking(False)
    selectorObj.register(clientSock, selectors.EVENT_READ, clientRead)


if __name__ == "__main__":
    sel = selectors.DefaultSelector()
    # For regular TCP socket
    sel.register(createServerSocket(('0.0.0.0', 9001)),
                 selectors.EVENT_READ,
                 acceptClientSocket)
    # For SSL TCP socket
    sel.register(createServerSocket(('0.0.0.0', 9002)),
                 selectors.EVENT_READ,
                 acceptSslClientSocket)

    print("Entering event loop. Wait for connection.")
    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(sel, key.fileobj, mask)
