#!/usr/bin/env python3
# coding: utf-8
# Copyright 2021 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Debangana Ghosh
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, headers = "", body=""):
        self.code = code
        self.body = body
        self.headers = headers

class HTTPClient(object):
    def get_host_port(self,url):
        """
        parse host, path and port from url
        has default values for port and path if not declared in url
        cited: https://docs.python.org/3/library/urllib.parse.html
        """
        components = urllib.parse.urlparse(url)
        port = 80
        if 'http' not in components.scheme and 'https' not in components.scheme:
            components = urllib.parse.urlparse('http://'+url)
        path = components.path
        if path == '':
            path = '/'
        if components.port:
            port = components.port
        host = components.hostname
        return (host, path, port)

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        """
        param: data - HTTP Response
        returns: status code
        """
        return int(data.split(' ')[1])

    def get_headers(self,data):
        """
        param: data - HTTP Response
        returns: headers
        """
        return data.split('\r\n\r\n')[0]

    def get_body(self, data):
        """
        print everything after headers
        """
        return data[data.index('\r\n\r\n'):]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host, path, port = self.get_host_port(url)

        self.connect(host, int(port))
        data = "GET {} HTTP/1.1\r\nHost: {}:{}\r\nAccept-Charset: UTF-8\r\nConnection: close\r\n\r\n".format(path, host, port)
        self.sendall(data)

        res = self.recvall(self.socket)
        code = self.get_code(res)
        body = self.get_body(res)
        headers = self.get_headers(res)
        self.close()
        return HTTPResponse(code, headers, body)

    def POST(self, url, args=None):
        """
        "Serializing dictionaries into query strings" from
        http://www.compciv.org/guides/python/how-tos/creating-proper-url-query-strings/#what-is-a-url-query-string

        "Formatting post queries" from
        https://www.w3schools.com/tags/ref_httpmethods.asp

        "How are parameters sent in a post request?" from https://stackoverflow.com/questions/14551194/how-are-parameters-sent-in-an-http-post-request
        answer from https://stackoverflow.com/users/69083/guffa
        """
        host, path, port = self.get_host_port(url)
        if args:
            args = urllib.parse.urlencode(args)
        elif not args:
            args = ''
        self.connect(host, int(port))
        full_query = "POST {} HTTP/1.1\r\nHost: {}:{}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}".format(path, host, port, len(args.encode('utf-8')), args)
        # print(full_query)
        self.sendall(full_query)
        res = self.recvall(self.socket)
        code = self.get_code(res)
        body = self.get_body(res)
        headers = self.get_headers(res)
        self.close()
        return HTTPResponse(code, headers, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            result = self.POST( url, args )
        else:
            result = self.GET( url, args )
        print("Code: {}\n\r\nHeaders: \n{}\n\nBody: {}".format(result.code, result.headers, result.body))
        return result

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
