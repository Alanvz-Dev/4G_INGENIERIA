import http.client as httplib
from xmlrpc import client as xmlrpc_client

class TimeoutTransport(xmlrpc_client.Transport):
    def set_timeout(self, timeout):
        self.timeout = timeout
    def make_connection(self, host):        
        return httplib.HTTPConnection(host, timeout=self.timeout)