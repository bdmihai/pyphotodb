""" pyphotodb - import
Copyright (C) 2010-2016 B.D. Mihai.

This file is part of pyphotodb.

pyphotodb  is  free  software:  you  can redistribute it and/or modify it
under the terms of the GNU Lesser Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

pyphotodb  is  distributed  in  the  hope  that  it  will be  useful,  but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser Public License for
more details.

You should have received a copy of the GNU Lesser Public License along
with pyphotodb.  If not, see http://www.gnu.org/licenses/."""

import os
import sys
import argparse
import sqlite3
import logging
import datetime
import shutil
import hashlib
import exifread

class Photo:
    def __init__(self, file_path):
        self.file = file_path
        self.hash = hashlib.md5(open(self.file, 'rb').read()).hexdigest()
        self.size = os.path.getsize(self.file)
        self.idet = 0
        self.name = ''
        self.datetime = datetime.datetime.now()
        self.extension = ''
        self.make = ''
        self.model = ''
        self.software = ''
        self.width = 0
        self.height = 0
        self.orientation = ''
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0

    def get_properties(self):
        tags = exifread.process_file(open(self.file, 'rb'))
        self.datetime = self.get_photo_datetime(tags)
        self.make = self.get_photo_make(tags)
        self.model = self.get_photo_model(tags)
        self.software = self.get_photo_software(tags)
        self.width = self.get_photo_width(tags)
        self.height = self.get_photo_height(tags)
        self.orientation = self.get_photo_orientation(tags)
        self.latitude = self.get_photo_latitude(tags)
        self.longitude = self.get_photo_longitude(tags)
        self.altitude = self.get_photo_altitude(tags)
        _, self.extension = os.path.splitext(self.file.lower())
        self.name = '{0}-{1:0>2d}-{2:0>2d}-{3:0>6X}{4}'.format(self.datetime.year, self.datetime.month, self.datetime.day, self.idet, self.extension)

    def get_photo_make(self, tags):
        make = ''
        if (tags):
            if ('Image Make' in tags):
                try:
                    make = tags['Image Make'].printable
                except Exception as e:
                    logging.info(e)
        return make

    def get_photo_model(self, tags):
        model = ''
        if (tags):
            if ('Image Model' in tags):
                try:
                    model = tags['Image Model'].printable
                except Exception as e:
                    logging.info(e)
        return model

    def get_photo_software(self, tags):
        software = ''
        if (tags):
            if ('Image Software' in tags):
                try:
                    software = tags['Image Software'].printable
                except Exception as e:
                    logging.info(e)
        return software

    def get_photo_datetime(self, tags):
        dt = datetime.datetime.fromtimestamp(os.path.getmtime(self.file))
        if (tags):
            if ('Image DateTime' in tags):
                try:
                    org_timestamp = datetime.datetime.strptime(tags['Image DateTime'].printable, '%Y:%m:%d %H:%M:%S')
                    if (org_timestamp < dt):
                        dt = org_timestamp
                except Exception as e:
                    logging.info(e)
        return dt

    def get_photo_width(self, tags):
        width = 0
        if (tags):
            if ('EXIF ExifImageWidth' in tags):
                try:
                    width = tags['EXIF ExifImageWidth'].values[0]
                except Exception as e:
                    logging.info(e)
        return width

    def get_photo_height(self, tags):
        height = 0
        if (tags):
            if ('EXIF ExifImageLength' in tags):
                try:
                    height = tags['EXIF ExifImageLength'].values[0]
                except Exception as e:
                    logging.info(e)
        return height

    def get_photo_orientation(self, tags):
        orientation = ''
        if (tags):
            if ('Image Orientation' in tags):
                try:
                    orientation = tags['Image Orientation'].printable
                except Exception as e:
                    logging.info(e)
        return orientation

    def get_photo_latitude(self, tags):
        latitude = 0.0
        if (tags):
            if ('GPS GPSLatitude' in tags):
                try:
                    degrees = tags['GPS GPSLatitude'].values[0]
                    minutes = tags['GPS GPSLatitude'].values[1]
                    seconds = tags['GPS GPSLatitude'].values[2]
                    latitude = float(degrees.num)/float(degrees.den) + float(minutes.num)/float(minutes.den) * 1.0 / 60.0 + float(seconds.num/seconds.den) * 1.0 / 3600.0
                except Exception as e:
                    logging.info(e)
        return latitude

    def get_photo_longitude(self, tags):
        longitude = 0.0
        if (tags):
            if ('GPS GPSLongitude' in tags):
                try:
                    degrees = tags['GPS GPSLongitude'].values[0]
                    minutes = tags['GPS GPSLongitude'].values[1]
                    seconds = tags['GPS GPSLongitude'].values[2]
                    longitude = float(degrees.num)/float(degrees.den) + float(minutes.num)/float(minutes.den) * 1.0 / 60.0 + float(seconds.num/seconds.den) * 1.0 / 3600.0
                except Exception as e:
                    logging.info(e)
        return longitude

    def get_photo_altitude(self, tags):
        altitude = 0.0
        if (tags):
            if ('GPS GPSAltitude' in tags):
                try:
                    alt = tags['GPS GPSAltitude'].values[0]
                    altitude = float(alt.num)/float(alt.den)
                except Exception as e:
                    logging.info(e)
        return altitude

def main(argv):
    parser = argparse.ArgumentParser(prog='import.py')
    parser.add_argument('--rootPath', required=True, help='directory where the db is located')
    parser.add_argument('--importPath', required=True, help='directory from where the pictures shall be imported')
    parser.add_argument('--noLogo', action='store_true', help='do not show logo')
    options = parser.parse_args(argv[1:])

    if (options.noLogo == False):
        print('PyPhoto Database Import Version 2.0.0')
        print('Copyright (C) B.D.Mihai. All rights reserved.')

    # check the root directory
    options.rootPath = os.path.normpath(options.rootPath)
    if (os.path.isdir(options.rootPath) == False):
        print('ERROR: Directory ' + options.rootPath + ' does not exist!')
        return 1
    if (os.access(os.path.join(options.rootPath, 'database.s3db'), os.W_OK) == False):
        print('ERROR: Database from ' + options.rootPath + ' not writable!')
        return 1
    options.importPath = os.path.normpath(options.importPath)
    if (os.path.isdir(options.importPath) == False):
        print('ERROR: Directory ' + options.importPath + ' does not exist!')
        return 1
    options.filter = ('.jpg', '.jpeg', '.gif', '.png', '.bmp', '.tiff')

    # create logfile
    logging.basicConfig(filename = os.path.join(options.rootPath, 'log', datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S.import.log')), filemode = 'w', level = logging.INFO, format = '%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',)

    # open the database
    print('Importing photos', end = "")
    conn = sqlite3.connect(os.path.join(options.rootPath, 'database.s3db'))
    logging.info('Database: ' + os.path.join(options.rootPath, 'database.s3db'))

    # find all relevant files to be imported
    for root, _, files in os.walk(options.importPath):
        for name in files:
            _, extension = os.path.splitext(name.lower())
            # filter for allowed extensions
            if (extension in options.filter):
                photo = Photo(os.path.join(root, name))
                # check for duplicates
                if (is_not_duplicate(conn, photo)):
                    # read all photo informations
                    photo.idet = get_next_photo_id(conn)
                    photo.get_properties()
                    # store photo to database
                    add_to_bulk(options, photo)
                    add_to_photos(conn, photo)
                    add_to_albums(conn, photo, os.path.basename(options.importPath))
                    logging.info(photo.file + ' imported as ' + photo.name)
                    print('.', end = ""); sys.stdout.flush()
                else:
                    add_to_albums(conn, photo, os.path.basename(options.importPath))
                    logging.info(photo.file + ' duplicate. Not imported!')
                    print('-', end = ""); sys.stdout.flush()

    # close database
    conn.commit()
    conn.close()
    print('done')
    return 0

def get_next_photo_id(conn):
    idet = conn.cursor().execute('SELECT max(Photos.Id) FROM Photos').fetchone()[0]
    if (idet == None):
        idet = 1
    else:
        idet += 1
    return idet

def is_not_duplicate(conn, photo):
    c = conn.cursor()
    c.execute('SELECT Photos.Id,Photos.Name FROM Photos WHERE Photos.Hash=? AND Photos.Size=?', (photo.hash, photo.size))
    return c.fetchone() == None

def add_to_photos(conn, photo):
    c = conn.cursor()
    c.execute('INSERT INTO Photos (Id,Name,Hash,Size,DateTime,Make,Model,Software,Width,Height,Orientation,Latitude,Longitude,Altitude) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)', \
        ( \
            photo.idet, \
            photo.name, \
            photo.hash, \
            photo.size, \
            photo.datetime, \
            photo.make, \
            photo.model, \
            photo.software, \
            photo.width, \
            photo.height, \
            photo.orientation, \
            photo.latitude, \
            photo.longitude, \
            photo.altitude \
        ))
    return

def add_to_albums(conn, photo, album):
    c = conn.cursor()
    # get photo id
    c.execute('SELECT Photos.Id FROM Photos WHERE Photos.Hash=? AND Photos.Size=?', (photo.hash, photo.size))
    photo_id = c.fetchone()[0]
    # check if already in albums
    c.execute('SELECT Count() FROM Albums where Albums.Name=? and Albums.PhotoId=?', (album, photo_id))
    photo_link_count = c.fetchone()[0]
    if (photo_link_count == 0):
        c.execute('INSERT INTO Albums (Name,PhotoId) VALUES(?,?)', (album, photo_id))
    return

def add_to_bulk(options, photo):
    shutil.copy2(photo.file, os.path.join(options.rootPath, 'bulk', photo.name))
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv))