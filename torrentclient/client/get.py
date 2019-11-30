import os
import bencode
import requests
import socket
import hashlib

from torf import Torrent


def get_content(torrent_path: str):
    t = Torrent.read(filepath=torrent_path)
    bcode = bencode.bread(torrent_path)
    hash_info = hashlib.sha1(bencode.bencode(bcode['info'])).digest()
    peer_id = "-{}{}{}-".format(
        'BT', '1000', str(os.getpid()).zfill(12),
    )
    if 'length' in bcode['info']:
        left = bcode['info']['length']
    else:
        left = 0
        for file in bcode['info']['files']:
            left += file['length']
    for tracker in t.trackers:
        print(tracker)
        url_split = tracker[0].split(":")
        #print(url_split)
        url = ":".join(url_split[:-1])
        #port = url_split[-1].split("/announce")[0]
        try:
            s = socket.socket()
            s.connect((url.strip("http://"), 80))
        except socket.gaierror as e:
            print("failed to open socket to {}:{}".format(url, 80))
            continue
        except Exception as e:
            print("Unexpected exception: {}".format(e))
            continue
        else:
            print("\nsuccess\n")
        print("\nHTTP GET\n")
        for port in range(6881, 6889+1):
            try:
                response = requests.get(
                    url=url,#tracker[0],
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
            print(response.__dict__)
            print()
            print(response.text)
            print()
            if response.status_code == 200:
                print("success!")