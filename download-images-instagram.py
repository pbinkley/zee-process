#!/usr/bin/env python3

import os
import sys
import ndjson
import csv
from datetime import datetime
from urllib.parse import urlparse
import urllib.request
from pathlib import Path
import time
import re

import pdb

# this script reads an Instagram ndjson file produced by Zeeschuimer,
# and downloads the images into data/images/instagram

# note: media have three possible types: IMAGE, VIDEO, or CAROUSEL_ALBUM
# (https://developers.facebook.com/docs/instagram-basic-display-api/reference/media/)
# In the ndjson we find numeric values (1) - I'm assuming this is IMAGE

# Download directory structure: need to break up an 11,000 image collection
# into subdirectories. So: use the last two digits of the item_id as the subdir. So for item_id
# 2991135982891617086_528817151 and image url
# https://instagram.fyyc7-1.fna.fbcdn.net/v/t51.2885-15/319097383_6043389685693303_7973036991037479223_n.jpg?stp=dst-jpg_e35&_nc_ht=instagram.fyyc7-1.fna.fbcdn.net&_nc_cat=1&_nc_ohc=0R_dvTHS9ggAX_Hbb_f&edm=AJ9x6zYBAAAA&ccb=7-5&ig_cache_key=Mjk5MTEzNTk3MjgwODU5NDgyMA%3D%3D.2-ccb7-5&oh=00_AfD4imQRq8xa0Wix-CnqZ59HzxrTorkmkmcWh9Y_qJTpxg&oe=639D8E50&_nc_sid=cff2a4
# the file would be stored as data/images/instagram/51/319097383_6043389685693303_7973036991037479223_n.jpg

# collect fields for images csv:
# item_id, timestamp, subdir, image filename, width, height, download timestamp

if len(sys.argv) <= 1:
  print('Provide path/name of ndjson file')
  sys.exit()

filename = sys.argv[1]

# set delay between downloads; default: 10 seconds
delay = 10 # TODO allow override with argument

# regex for getting subdir
subdir_regex = re.compile(r".+(\d{2})_.+")

print(filename)

with open(filename) as f:
  data = ndjson.load(f)
  itemcount = len(data)
  print("%s items; %s hours total download time" % (len(data), "{:.2f}".format(len(data) * delay / 60 / 60)))

  counter = 1
  for record in data:
    item_id = record['item_id']
    code = record['data']['code']
    media_type = record['data']['media_type']
    print("%s/%s: %s %s (%s)" % (counter, itemcount, item_id, code, media_type))
    subdir = "data/images/instagram/%s" % subdir_regex.sub(r'\1', item_id)
    imagerecord = ''
    if 'carousel_media' in record['data']:
      imagerecord = record['data']['carousel_media'][0]['image_versions2']['candidates'][0]
    else:
      imagerecord = record['data']['image_versions2']['candidates'][0]
    imageurl = imagerecord['url']

    parts = urlparse(imageurl)
    directories = parts.path.strip('/').split('/')    
    filename = directories[-1]
    fileext = filename.split('.')[-1]

    # does image exist?
    filepath = "%s/%s" % (subdir,"%s.%s" % (item_id, fileext))
    fileexists = Path(filepath).is_file()
    if not fileexists:
      if not Path(subdir).is_dir():
        os.makedirs(subdir)
      urllib.request.urlretrieve(imageurl, filepath)

      # pause for delay
      time.sleep(delay)

    counter += 1

print('done')