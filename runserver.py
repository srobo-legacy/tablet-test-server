#!/usr/bin/env python2

import SimpleHTTPServer
import SocketServer
SimpleHTTPServer.SimpleHTTPRequestHandler.extensions_map['.webapp'] = 'application/x-web-app-manifest+json'
httpd = SocketServer.TCPServer(("", 8000), SimpleHTTPServer.SimpleHTTPRequestHandler)
httpd.serve_forever()
