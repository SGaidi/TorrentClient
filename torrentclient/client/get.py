import re
import os
import bencode
import requests
import socket
import hashlib

from torf import Torrent


def get_content(torrent_path: str):
    DEFAULT_INTERVAL = 1000  # seconds
    t = Torrent.read(filepath=torrent_path)
    bcode = bencode.bread(torrent_path)
    hash_info = hashlib.sha1(bencode.bencode(bcode['info'])).digest()
    peer_id = "-{}{}{}-".format('BT', '1000', str(os.getpid()).zfill(12))
    if 'length' in bcode['info']:
        left = bcode['info']['length']
    else:
        left = 0
        for file in bcode['info']['files']:
            left += file['length']
    for tracker in t.trackers:
        print(tracker)
        match = re.match(r"(?P<protocol>wss|http|udp)://(?P<hostname>[.\w]+)(:(?P<port>[0-9]+))?(/announce)?", tracker[0])
        if match is None:
            raise RuntimeError("Could not match: {}".format(tracker[0]))
        protocol = match.group("protocol")
        if protocol != "http":
            print("Unsupported protocol ({})".format(protocol))
            continue
        hostname = match.group("hostname")
        port = match.group("port")
        print("protocol={}, hostname={}, port={}".format(protocol, hostname, port))
        try:
            s = socket.socket()
            s.connect((hostname, 80))
        except socket.gaierror as e:
            print("Failed to open socket to {}:{}".format(hostname, 80))
            continue
        except Exception as e:
            print("Unexpected exception: {}".format(e))
            continue
        for port in range(6881, 6882):#6889+1):
            # TODO: check port is not taken in local machine
            try:
                response = requests.get(
                    url=tracker[0],
                    params={
                        "info_hash":    hash_info,
                        "peer_id":      peer_id,
                        "port":         str(port),
                        "uploaded":     "0",
                        "downloaded":   "0",
                        "left":         str(left),
                        "compact":      "1",
                        "event":        "started",
                    },
                )
            except requests.exceptions.ConnectionError as e:
                print(e)
                continue
            except Exception as e:
                print("Unexpected Exception {}".format(e))
                continue
            print("\n".join("{}={}".format(key, value) for key, value in response.__dict__.items()))
            print()
            try:
                text = response.text
            except UnicodeEncodeError:
                print("Wrong encoding")
                response.encoding = response.apparent_encoding
                text = response.text.encode('utf-8')
            print()
            if response.status_code != 200:
                print("Failure. HTTP response {}".format(response.status_code))
                continue
            if response.headers['Content-Type'] != "text/plain" and response.headers['Content-Type'] != "application/octet-stream":
                print("Invalid Content-Type ({}), not 'text/plain' or 'application/octet-stream'".format(response.headers['Content-Type']))
                continue
            if isinstance(text, bytes):
                print("DEBUG")
                text = text.decode("utf-8")
            elif not isinstance(text, str):
                print("Invalid response text type ({}), not str".format(type(text).__name__))
                continue
            from urllib.parse import quote_from_bytes, unquote
            match = re.match(r"(?P<left>.*)5:peers(?P<length>\d+):(?P<right>.*)$", text)
            if not match:
                print("Could not match response with peers: {}".format(text))
                continue
            print(response._content)
            left_response = match.group("left")
            peers_len = int(match.group("length"))
            peers = match.group("right")[:peers_len]
            right_response = match.group("right")[peers_len:]
            print("left_response={}".format(left_response))
            print("peers_len={}".format(peers_len))
            print("peers={}".format(peers))
            print("right_response={}".format(right_response))
            # quote_from_bytes(peers)
            peerless_response = left_response + right_response
            print("peerless_response={}".format(peerless_response))
            response = bencode.bdecode(peerless_response.encode())
            if "failure reason" in response:
                print("Failure: {}".format(response["failure reason"]))
                continue
            if "warning message" in response:
                print("Warning: {}".format(response["warning message"]))
            print(response)
            print("success!")
            break
