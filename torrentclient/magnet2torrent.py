from torrentclient.torrent import Torrent
from torrentclient.magnetlink import MagnetLink


def magnet2torrent(magnet_link: MagnetLink) -> Torrent:
    ml_str = ""
    for tracker in magnet_link.address_tracker:
        ml_str += '&tr=' + tracker
    """

    # TODO: URN parser in separate class?
    #Create the torrent file name
    magnetName = magnetLink[magnetLink.find("btih:") + 1:magnetLink.find("&")]
    magnetName = magnetName.replace('tih:','')
    torrentfilename = 'meta-' + magnetName + '.torrent'
    # TODO: pass all these parameters to Torrent class
    # Write the magnet link to the torrent file
    with open(torrentfilename, 'w') as o:
        linkstr = u'd10:magnet-uri' + str(len(magnetLink)) + u':' + magnetLink + u'e'
        linkstr = linkstr.encode('utf8')
        o.write(linkstr)
    """

    return Torrent
