import re
import bencode
import logging
import requests

from torrentclient.client.peerinteract.peer import Peer


class HandleResponse:
    """Class for validating and extracting information from HTTP response from a Tracker"""

    VALID_CONTENT_TYPES = [None, "text/plain", "text/plain; charset=utf-8", "application/octet-stream"]
    # TODO: find a way to encode and decode back
    RESPONSE_PATTERN = re.compile(r"(?P<left>.*)5:peers(?P<length>\d+):(?P<right>.*)$")

    logger = logging.getLogger('handle-response')

    class Exception(Exception):
        """An exception with extracting information from HTTP response"""

    def __init__(self, response: requests.Response):
        self.response = response

    def __str__(self):
        return "HandleResponse({})".format(self.response)

    def __repr__(self):
        return {'response': self.response}

    def _validate_response(self):
        """validates status code and `Content-Type` header
        raises an exception if any of them are invalid"""
        if self.response.status_code != 200:
            raise HandleResponse.Exception("HTTP response status code {}".format(self.response.status_code))
        if 'Content-Type' in self.response.headers and \
                self.response.headers['Content-Type'] not in HandleResponse.VALID_CONTENT_TYPES:
            raise HandleResponse.Exception("Invalid Content-Type ({}), not in {}".format(
                self.response.headers.get('Content-Type', None), HandleResponse.VALID_CONTENT_TYPES))

    def _decode_response(self):
        """tries to decode according to BitTorrent protocol"""
        self.bresponse = bencode.bdecode(self.response.content)
        self.logger.info("bresponse={}".format(self.bresponse))
        if "failure reason" in self.bresponse:
            raise HandleResponse.Exception("Failure in response: {}".format(self.bresponse["failure reason"]))
        if "warning message" in self.bresponse:
            self.logger.warning("Warning in response: {}".format(self.bresponse["warning message"]))

    def _parse_peers_dict(self):
        try:
            peers_dict = bencode.bdecode(self.bresponse['peers'])
        except bencode.BencodeDecodeError as e:
            raise HandleResponse.Exception(e)
        # TODO: complete dictionary parsing

    def _parse_peers_bytes(self):
        import socket
        self.peers = []
        if len(self.bresponse['peers']) % 6 != 0:
            raise HandleResponse.Exception(
                "Invalid peers length ({}), not divisible by 6".format(len(self.bresponse['peers'])))
        for start_idx in range(0, len(self.bresponse['peers']), 6):
            peer_ip = ".".join(str(octet) for octet in self.bresponse['peers'][start_idx:start_idx+4])
            try:
                socket.inet_aton(peer_ip)
            except socket.error as e:
                self.logger.warning("Invalid IP address ({}): {}".format(peer_ip, e))
            peer_port = int.from_bytes(self.bresponse['peers'][start_idx+4:start_idx+6], byteorder="big", signed=False)
            self.peers.append(Peer(peer_ip, peer_port))

    def _parse_peers(self):
        """tries parsing peers from response using the 2 supported models"""
        try:
            self._parse_peers_dict()
        except HandleResponse.Exception as e:
            self.logger.debug("Assuming peers in response are in bytes mode")
            try:
                self._parse_peers_bytes()
            except HandleResponse.Exception as e:
                raise e
        self.logger.debug("peers=[{}]".format(", ".join(str(peer) for peer in self.peers)))

    def handle(self):
        self._validate_response()
        self._decode_response()
        # TODO: handle interval in response
        self._parse_peers()
        return self.peers