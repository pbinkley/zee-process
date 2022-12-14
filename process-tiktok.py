#!/usr/bin/env python3

import os
import sys
import ndjson
import csv
from datetime import datetime

import pdb
#pdb.set_trace()
if len(sys.argv) <= 1:
  print('Provide path/name of ndjson file')
  sys.exit()

filename = sys.argv[1]
# zeeschuimer-export-tiktok.com-2022-12-09T201420.ndjson
print(filename)

with open(filename) as f:
  data = ndjson.load(f)

# TODO calculate new fields here

header = ["id","thread_id","author","author_full","author_id","author_followers","body","timestamp","is_duet","music_name","music_id","music_url","video_url","tiktok_url","thumbnail_url","likes","comments","shares","plays","hashtags","stickers","warning","unix_timestamp"]

outputDir = 'data/output/tiktok'
if not os.path.isdir(outputDir):
  os.makedirs(outputDir)

with open('data/output/tiktok/output.csv', 'w', encoding='UTF8') as f:
  writer = csv.writer(f)
  writer.writerow(header)


  for record in data:
    #pdb.set_trace()
    recdata = record["data"]

    hashtags = []
    if "textExtra" in recdata:
      for h in recdata["textExtra"]:
        hashtags.append(h["hashtagName"])
    hashtags = ",".join(hashtags)

    stickerText = ""
    stickers = recdata["stickersOnItem"]
    if stickers:
      #pdb.set_trace()
      stickerText = ' '.join(stickers[0]["stickerText"])

#    recdata["stickersOnItem"]

    writer.writerow([
      int(record["item_id"]), # id
      int(record["item_id"]),  # thread_id TODO: confirm it's always the same as id
      recdata["author"]["uniqueId"], # author
      recdata["author"]["nickname"], # author_full
      int(recdata["author"]["id"]), # author_id]
      int(recdata["authorStats"]["followerCount"]), # author_followers
      recdata['desc'], # body
      datetime.fromtimestamp(recdata["createTime"]).isoformat(sep=" "), # timestamp
      bool(recdata["author"]["duetSetting"]), # id_duet TODO confirm source field
      recdata["music"]["title"], # music_name
      recdata["music"]["id"], # music_id
      recdata["music"]["playUrl"], # music_url
      "https://tiktok.com/@%s/video/%s" % (recdata["author"]["uniqueId"], int(record["item_id"])), # tiktok_url
      "D", # thumbnail_url
      int(recdata["stats"]["diggCount"]), # likes
      int(recdata["stats"]["commentCount"]), # comments
      int(recdata["stats"]["shareCount"]), # shares
      int(recdata["stats"]["playCount"]), # plays
      hashtags, # hashtags
      stickerText,
      recdata["createTime"]
    ])
