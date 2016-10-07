#!/bin/env python
# -*- coding: utf8 -*-

import random
import socketserver as SocketServer
import chardet
from pyicap3.pyicap import *
import select

class ThreadingSimpleServer(SocketServer.ThreadingMixIn, ICAPServer):
    pass

class ICAPHandler(BaseICAPRequestHandler):

    def example_OPTIONS(self):
        self.set_icap_response(200)
        self.set_icap_header('Methods', 'RESPMOD')
        self.set_icap_header('Service', 'example_RESPMOD')  
        self.set_icap_header('Preview', '1024')
        self.set_icap_header('Transfer-Preview', '*')
        self.set_icap_header('Transfer-Ignore', 'jpg,jpeg,gif,png,swf,flv')
        self.set_icap_header('Transfer-Complete', '')
        self.set_icap_header('Max-Connections', '100')
        self.set_icap_header('Options-TTL', '3600')
        self.send_headers(False)


    def handle_preview(self,buffer):
        if buffer:
            prevbuf = buffer
        else:
            prevbuf = ''.encode('utf-8')

        while True:
            chunk = self.read_chunk()
            if chunk ==  None:
                continue
            if self.ieof or self.eob:
                self.log_error("found end of object         ")
                break
            if self.is_it_empty_string(chunk):
                break
            prevbuf += chunk


        return prevbuf

    def is_it_empty_string(self,value):
        encoding = chardet.detect(value)['encoding']
        if encoding and value.decode(encoding,"replace") == '':
            return True
        if value.decode("utf-8",'ignore') == '':
            return True

    def example_RESPMOD(self):
        #while True:
        #    chunk = self.read_chunk()
        #    if chunk == '':
        #        break
        #self.send_enc_error(500, body='<html><head><title>Whoops</title></head><body><h1>500 ICAP meditation</h1></body></html>')
        #return
        self.set_icap_response(200)

        self.set_enc_status(' '.join(self.enc_res_status))
        for h in self.enc_res_headers:
            for v in self.enc_res_headers[h]:
                self.set_enc_header(h, v)
        params = {}
        params['request_headers'] = self.enc_req_headers
        params['request_headers'] = self.enc_res_headers

        # The code below is only copying some data.
        # Very convoluted for such a simple task.
        # This thing needs a serious redesign.
        # Well, without preview, it'd be quite simple...
        if not self.has_body:
            self.send_headers(False)
            return
        if self.preview:
            prevbuf = ''.encode("utf-8")
            prevbuf = self.handle_preview(prevbuf)
            if self.ieof:
                self.send_headers(True)
                if len(prevbuf) > 0:
                    self.write_chunk(prevbuf)
                self.write_chunk(''.encode("utf-8"))
                return
            self.cont()
            self.log_error("Continue")
            self.send_headers(True)
            if len(prevbuf) > 0:
                self.write_chunk(prevbuf)
            while True:
                chunk = self.read_chunk()
                if chunk == None:
                    continue
                self.write_chunk(chunk)
                if self.is_it_empty_string(chunk):
                    break

        else:
            self.send_headers(True)
            while True:
                chunk = self.read_chunk()
                if chunk == None:
                    continue
                self.write_chunk(chunk)
                if self.is_it_empty_string(chunk):
                    break



port = 13440

server = ThreadingSimpleServer(('', port), ICAPHandler)
try:
    while 1:
        server.handle_request()
except KeyboardInterrupt:
    print ("Finished")
