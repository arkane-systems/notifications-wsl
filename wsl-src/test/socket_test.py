#! /bin/env python3

import socket

def entrypoint():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    sock.connect('/mnt/c/Users/avatar/wslnote.sock')
    sock.send ('This is a test.\u0004')
    sock.close ()

entrypoint()
