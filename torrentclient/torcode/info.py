from torrentclient.meta.paramclass import ParamClass
from torrentclient.meta.defineparam import DefineParams


class InfoParent(ParamClass):

    dp = DefineParams([
        ('piece_length',    "number of bytes in each piece"),
        ('pieces',          "string consisting of the concatenation of all 20-byte SHA1 hash values, one per piece"),
        ('private',         "If it is set to \"1\", the client MUST publish its presence to get other peers ONLY via " +
                            "the trackers explicitly described in the metainfo file. If this field is set to \"0\"" +
                            "or is not present, the client may obtain peer from other means, e.g. PEX peer exchange, " +
                            "dht"),
    ])


class InfoSingle(InfoParent):

    dp = InfoParent.dp.extend([
        ('name',    "filename"),
        ('length',  "length of the file in bytes"),
        ('md5sum',  "32-character hexadecimal string corresponding to the MD5 sum of the file"),
    ])


class InfoMultiple(InfoParent):

    dp = InfoParent.dp.extend([
        ('name',    "the name of the directory in which to store all the files"),
        ('files',   "list of dictionaries, one for each file"),
    ])
