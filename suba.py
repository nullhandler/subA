import struct
import os
import sys
import requests
import json
import gzip
import shutil

# © Selva

def getHash(filepath, size):
    # Taken from opensubtitles docs
    longlongformat = 'q'  
    bytesize = struct.calcsize(longlongformat)

    try:
        f = open(filepath, "rb")
    except(IOError):
        return "IOError"

    hash = int(size)

    if int(size) < 65536 * 2:
        return "SizeError"

    for _ in range(65536 // bytesize):
        buffer = f.read(bytesize)
        (l_value, ) = struct.unpack(longlongformat, buffer)
        hash += l_value
        hash = hash & 0xFFFFFFFFFFFFFFFF  # to remain as 64bit number

    f.seek(max(0, int(size) - 65536), 0)
    for _ in range(65536 // bytesize):
        buffer = f.read(bytesize)
        (l_value, ) = struct.unpack(longlongformat, buffer)
        hash += l_value
        hash = hash & 0xFFFFFFFFFFFFFFFF

    f.close()
    returnedhash = "%016x" % hash
    return str(returnedhash)

if os.path.exists(sys.argv[-1]):
    size = os.path.getsize(sys.argv[-1])
    fileHash = getHash(sys.argv[-1], size)
    url = f'https://rest.opensubtitles.org/search/moviebytesize-{size}/moviehash-{fileHash}/sublanguageid-eng'
    req = requests.get(url, headers={'User-agent': 'TemporaryUserAgent'})
    # for ele in json.loads(req.content):
    #     print(ele['SubFileName'] + ele['ZipDownloadLink'])
    js = json.loads(req.content)
    subResponse = requests.get(js[0]['SubDownloadLink'], allow_redirects=True)
    zipPath = os.path.dirname(sys.argv[-1]) + '/subA.zip'
    print(zipPath)
    open(zipPath, 'wb').write(subResponse.content)
    with gzip.open(zipPath, 'rb') as f_in:
        with open(os.path.splitext(sys.argv[-1])[0] + '.srt', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(zipPath)
    print('Subtitle Downloaded')

