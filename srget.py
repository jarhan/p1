import sys
import socket as skt
import os
from urlparse import urlparse

class Downloader():

    def __init__(self):
        self.url = ""
        self.port = 80
        self.filename = ""
        self.path = "/Users/Pwtk/Downloads"
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
        self.getheader = ""
        self.all = ""
        self.header = ""
        self.leftover = ""
        self.data = ""
        self.conlength = 0

    def connect(self):
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
        self.socket.connect((self.url, self.port))

    # send request to server
    def GET_header(self):
        self.getheader = "GET " + self.path + " HTTP/1.1\r\n" + "Host: " + self.url + "\r\n\r\n"
        self.socket.send(self.getheader)

    # extract content length from the header then cut it from the actual data
    def receive(self):
        # self.all = ""
        while True:
            rcv = self.socket.recv(1024)
            if not rcv: break
            self.all += rcv
            if "\r\n\r\n" in all:
                self.get_header(all)
                # self.conlength = self.get_contentlength()
                self.get_contentlength()
                break

        while len(self.data) < self.conlength:
            with open(os.path.join(self.path, self.filename), 'wb') as f:
                f.write(self.leftover)
                while True:
                    data = self.socket.recv(1024)
                    if not data: break
                    f.write(data)

    def get_header(self, sth):
        self.header, self.leftover = sth.split("\r\n\r\n")

    def get_contentlength(self):
        before, after = self.header.split("Content-Length: ")
        num, left = after.split("\r\n")
        self.conlength = int(num)

    def DocEx(self, input):
        # p = Downloader()
        # print input
        self.filename = input[2]
        ongoing = input[-1]
        slp = urlparse(ongoing)
        self.url = slp.hostname
        if type(slp.port) == str: self.port = int(slp.port)
        self.connect()
        self.GET_header()
        self.receive()
        self.socket.close()


if __name__ == '__main__':
    input = sys.argv
    download = Downloader()
    download.DocEx(input)


