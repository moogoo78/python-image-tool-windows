'''
key: {timestamp}:{hash[:6]}
'''

from datetime import datetime
import time
import os
import json
import sqlite3
import hashlib

import base64
import struct
import time
import pathlib

from .helpers import (
    Image,
    Database
)

IGNORE_FILES = ['Thumbs.db', '']
IMAGE_EXTENSIONS = ['.JPG', '.JPEG', '.PNG']

def _check_image_filename(dirent):
    _, fext = os.path.splitext(dirent.path)
    if fext.upper() in IMAGE_EXTENSIONS:
        return True
    return False


class Source(object):
    db = None

    def __init__(self, source_type, name=''):
        if source_type == 'database' and name:
            db = Database(name)
            self.db = db

    def from_folder(self, path):
        #thumpy = Thumpy(thumb_dir, dir_path, is_debug)
        with os.scandir(path) as it:
            image_list = []
            count = 0

            for entry in it:
                if not entry.name.startswith('.') and \
                   entry.is_file() and \
                   _check_image_filename(entry):
                    count += 1
                    img = Image(entry.path)
                    image_list.append({
                        'path': entry.path,
                        'name': entry.name,
                        'img': img,
                    })

            # insert into database
            ts_now = int(time.time())
            if self.db:
                dir_name = os.path.split(path)[-1]
                key_prefix = str(int(time.time()))

                sql = "INSERT INTO source (source_type, path, name, count, created) VALUES('folder', '{}', '{}', {}, {})".format(path, dir_name, count, ts_now)
                rid = self.db.exec_sql(sql, True)
                timestamp = None
                for i in image_list:
                    exif  = i['img'].exif
                    dtime = exif.get('DateTimeOriginal', '')
                    via = 'exif'
                    if dtime:
                        dt = datetime.strptime(exif.get('DateTime', ''), '%Y:%m:%d %H:%M:%S')
                        timestamp = dt.timestamp()
                    else:
                        stat = i['img'].get_stat()
                        timestamp = int(stat.st_mtime)
                        via = 'mtime'

                    sql = "INSERT INTO image (path, name, timestamp, timestamp_via, status, annotation, changed, exif, source_id) VALUES ('{}','{}', {}, '{}', 'I','{}', {}, '{}', {})".format(
                        i['path'],
                        i['name'],
                        timestamp,
                        via,
                        '',
                        ts_now,
                        json.dumps(exif),
                        rid)
                    self.db.exec_sql(sql)
                self.db.commit()
            self.db.close()

            return {}
