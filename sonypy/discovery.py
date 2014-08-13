import socket
import re
import requests


from .camera import Camera


SSDP_ADDR = '239.255.255.250'
SSDP_PORT = 1900
SSDP_MX = 1


discovery_msg = ('M-SEARCH * HTTP/1.1\r\n'
                 'HOST: %s:%d\r\n'
                 'MAN: "ssdp:discover"\r\n'
                 'MX: %d\r\n'
                 'ST: urn:schemas-sony-com:service:ScalarWebAPI:1\r\n'
                 '\r\n')


dd_regex = ('<av:X_ScalarWebAPI_ServiceType>'
            '(.+?)'
            '</av:X_ScalarWebAPI_ServiceType>'
            '<av:X_ScalarWebAPI_ActionList_URL>'
            '(.+?)'
            '</av:X_ScalarWebAPI_ActionList_URL>')


class Discoverer(object):
    camera_class = Camera

    @staticmethod
    def _parse_ssdp_response(data):
        lines = data.rstrip('\r\n').split('\r\n')
        assert lines[0] == 'HTTP/1.1 200 OK'
        headers = {}
        for line in lines[1:]:
            key, val = line.split(': ', 1)
            headers[key.lower()] = val
        return headers

    def _ssdp_discover(self, timeout=1, ip=None):
        socket.setdefaulttimeout(timeout)

        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_DGRAM,
                             socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET,
                        socket.SO_REUSEADDR,
                        1)
        sock.setsockopt(socket.IPPROTO_IP,
                        socket.IP_MULTICAST_TTL,
                        2)
        if ip:
            sock.setsockopt(socket.IPPROTO_IP,
                            socket.IP_MULTICAST_IF,
                            socket.inet_aton(ip))

        for _ in range(2):
            msg = discovery_msg % (SSDP_ADDR, SSDP_PORT, SSDP_MX)
            sock.sendto(msg.encode(), (SSDP_ADDR, SSDP_PORT))

        try:
            data = sock.recv(1024).decode()
        except socket.timeout:
            print('SOCKET TIMEOUT')
            pass
        else:
            print('*****')
            print(data)
            yield self._parse_ssdp_response(data)

    @staticmethod
    def _parse_device_definition(doc):
        """
        Parse the XML device definition file.
        """
        services = {}
        for m in re.findall(dd_regex, doc):
            service_name = m[0]
            endpoint = m[1]
            services[service_name] = endpoint + '/' + service_name
        return services

    def _read_device_definition(self, url):
        """
        Fetch and parse the device definition, and extract the URL endpoint for
        the camera API service.
        """
        r = requests.get(url)
        services = self._parse_device_definition(r.text)
        return services['camera']

    def discover(self, ip=None):
        cameras = []
        for resp in self._ssdp_discover(ip=ip):
            url = resp['location']
            endpoint = self._read_device_definition(url)
            camera = self.camera_class(endpoint)
            cameras.append(camera)
        return cameras
