import sys
from socket import socket,AF_INET,SOCK_STREAM
from urlparse import urlparse
import os

class Downloader():

    def __init__(self):
        self.host = ""
        self.port = 80
        self.filename = ""
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.header_connect = ""
        self.resume_request = ""
        self.header = ""
        self.leftover = ""
        self.curr_bytes = 0
        self.path = ""
        self.NL = "\r\n"

        self.lastMod = ""
        self.conlength = 0
        self.ETag = ""

        self.OlastMod = ""
        self.Oconlength = 0
        self.OETag = ""

        self.masur = ".LYdownload"

    # check boolean show that file is already exited or not
    def check_filepath(self):
        path = os.path.realpath(__file__).split(__file__)[0]
        return os.path.isfile(path + self.filename + self.masur)

    def connect(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print "Connecting to server"

    # send request to server
    def make_request(self):
        self.header_connect = "GET " + self.connect_path + " HTTP/1.1" + self.NL + "Host: " + self.host + self.NL + self.NL
        self.socket.send(self.header_connect)

    def make_resume(self):
        self.resume_request = "GET " + self.connect_path + " HTTP/1.1" + self.NL + "Host: " + self.host + self.NL + "Range: bytes=" + str(self.curr_bytes) + "-" + str(self.Oconlength) + self.NL + self.NL
        self.socket.send(self.resume_request)

    # extract content length from the header then cut it from the actual data
    def download(self):
        buffer = ""
        while True:
            rcv = self.socket.recv(8096)
            if not rcv: break
            buffer += rcv

            if self.NL + self.NL in buffer:
                self.get_header(buffer)
                forCheck = self.get_fromHeader(self.header)
                self.conlength = int(forCheck[0])
                self.lastMod = forCheck[1]
                self.ETag = forCheck[2]
                info = '{}: {}{}{}: {}{}{}: {}{}'.format('Content-Length', self.conlength, self.NL, 'Last-Modified', self.lastMod, self.NL, 'ETag', self.ETag, self.NL)
                break


        self.conlength, self.lastMod, self.ETag, info = self.start()

        print "Received header"

        try:
            # header with Content-Length
            if self.conlength != 0:
                with open(self.filename + self.masur, 'wb+') as f, open("info.txt", 'wb+') as dw:
                    f.write(self.leftover)
                    size = len(self.leftover)
                    dw.write(info)
                    while size < self.conlength:
                        atad = self.socket.recv(8096)
                        size += len(atad)
                        f.write(atad)
                        dw.write('{}{}'.format(size, self.NL))

            # header without Content-Length
            else:
                with open(self.filename + self.masur, 'wb+') as f, open("info.txt", 'wb+') as dw:
                    f.write(self.leftover)
                    dw.write(info)
                    while True:
                        buff = self.socket.recv(8096)
                        if not buff:
                            break
                        f.write(buff)

            os.renames(self.filename + self.masur, self.filename)

            f.close()
            os.remove("info.txt")
            print "Data saved"
            self.socket.close()
            sys.exit()

            print "Socket closed"

        except KeyboardInterrupt:
            print "    Download failed"
            sys.exit()

    def resume(self):
        buffer = ""
        while True:
            rcv = self.socket.recv(8096)
            if not rcv: break
            buffer += rcv

            if self.NL + self.NL in buffer:
                self.get_header(buffer)
                forCheck = self.get_fromHeader(self.header)
                self.Oconlength = int(forCheck[0])
                self.OlastMod = forCheck[1]
                self.OETag = forCheck[2]
                break

        print " Start Resuming"

        try:
            with open(self.filename + self.masur, 'a') as ad, open("info.txt", 'a') as ndw:
                nsize = self.curr_bytes
                total = self.curr_bytes + self.Oconlength
                while nsize < total:
                    atad = self.socket.recv(8096)
                    nsize += len(atad)
                    ad.write(atad)
                    ndw.write('{}{}'.format(nsize, self.NL))

            os.renames(self.filename + self.masur, self.filename)

            ad.close()
            os.remove("info.txt")
            print "Data saved"
            self.socket.close()
            sys.exit()

            print "Socket closed"

        except KeyboardInterrupt:
            print "    Resumed Interrupted"

    # for checking that file modified or not
    def check_similar(self):
        with open("info.txt", 'r') as rd:
            read = rd.read()
            self.curr_bytes = int(read.split("\r\n")[-2])
            old = self.get_fromHeader(read)
            self.Oconlength = old[0]
            self.OlastMod = old[1]
            self.OETag = old[2]
        return self.Oconlength == self.conlength and self.OlastMod == self.lastMod and self.OETag == self.ETag

    def get_header(self, sth):
        space = self.NL + self.NL
        splitted = sth.split(space)
        self.header = splitted[0]
        if len(splitted) > 2: self.leftover = space.join(splitted[1:])
        else: self.leftover = splitted[-1]

    def get_fromHeader(self, header):
        splitted = header.split(self.NL)
        cl = ''
        lm = ''
        et = ''
        for each in splitted:
            if "Content-Length" in each:
                word, cl = each.split(" ")
            if "Last-Modified" in each:
                word, lm = each.split(": ")
            if "ETag" in each:
                word, et = each.split(" ")
        return cl, lm, et

    def DocEx(self, input):
        self.filename = input[2]
        url = input[-1] # url:port
        url_component = urlparse(url)
        self.connect_path = url_component.path
        self.host = url_component.hostname
        if url_component.port != None:
            self.port = int(url_component.port)
        self.connect()
        if self.check_filepath():
            if not self.check_similar():
                # can resume immediately
                self.make_resume()
                self.resume()
            else:
                # something changed
                print "File is unable to resume. The program will re-download file for you."
                self.make_request()
                self.download()
            # resume
        else:
            # start downloading
            self.make_request()
            self.download()

if __name__ == '__main__':
    input = sys.argv
    download = Downloader()
    download.DocEx(input)