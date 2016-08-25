""" pyphotodb - link
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

def main(argv):
    parser = argparse.ArgumentParser(prog='import.py')
    parser.add_argument('--rootPath', required=True, help='directory where the db is located')
    parser.add_argument('--by', required=True, help='criteria used to perform the symbolic link')
    parser.add_argument('--noLogo', action='store_true', help='do not show logo')
    options = parser.parse_args(argv[1:])

    if (options.noLogo == False):
        print('PyPhoto Database Link Version 2.0.0')
        print('Copyright (C) B.D.Mihai. All rights reserved.')

    # check the root directory
    options.rootPath = os.path.normpath(options.rootPath)
    if (os.path.isdir(options.rootPath) == False):
        print('ERROR: Directory ' + options.rootPath + ' does not exist!')
        return 1
    if (os.access(os.path.join(options.rootPath, 'database.s3db'), os.R_OK) == False):
        print('ERROR: Database from ' + options.rootPath + ' not readable!')
        return 1
    options.posible_link = ('date', 'album')
    if (options.by not in options.posible_link):
        print('ERROR: Cannot link by ' + options.by + '!')
        return 1

    # create logfile
    logging.basicConfig(filename = os.path.join(options.rootPath, 'log', datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S.link.log')), filemode = 'w', level = logging.INFO, format = '%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',)

    # open the database
    print('Linking photos', end = "")
    conn = sqlite3.connect(os.path.join(options.rootPath, 'database.s3db'))
    logging.info('Database: ' + os.path.join(options.rootPath, 'database.s3db'))
    logging.info('Linking by: ' + options.by)

    if (options.by == 'album'):
        if (os.path.exists(os.path.join(options.rootPath, 'sort', 'by_album')) == False):
            os.mkdir(os.path.join(options.rootPath, 'sort', 'by_album'))
        c = conn.cursor()
        c.execute('SELECT Photos.Name,Albums.Name FROM Photos INNER JOIN Albums ON Photos.Id = Albums.PhotoId')
        for photo, album in c:
            if (os.path.exists(os.path.join(options.rootPath, 'sort', 'by_album', album)) == False):
                os.mkdir(os.path.join(options.rootPath, 'sort', 'by_album', album))
            if (os.path.exists(os.path.join(options.rootPath, 'sort', 'by_album', album, photo)) == False):
                os.symlink(os.path.join(options.rootPath, 'bulk', photo), os.path.join(options.rootPath, 'sort', 'by_album', album, photo))
                logging.info(photo + ' linked in ' + album)
                print('.', end = ""); sys.stdout.flush()
            else:
                print('-', end = ""); sys.stdout.flush()

    if (options.by == 'date'):
        if (os.path.exists(os.path.join(options.rootPath, 'sort', 'by_date')) == False):
            os.mkdir(os.path.join(options.rootPath, 'sort', 'by_date'))
        c = conn.cursor()
        c.execute('SELECT Photos.Name,Photos.DateTime FROM Photos')
        for photo, date in c:
            date = date[0:date.find(' ')]
            if (os.path.exists(os.path.join(options.rootPath, 'sort', 'by_date', date)) == False):
                os.mkdir(os.path.join(options.rootPath, 'sort', 'by_date', date))
            if (os.path.exists(os.path.join(options.rootPath, 'sort', 'by_date', date, photo)) == False):
                os.symlink(os.path.join(options.rootPath, 'bulk', photo), os.path.join(options.rootPath, 'sort', 'by_date', date, photo))
                logging.info(photo + ' linked in ' + date)
                print('.', end = ""); sys.stdout.flush()
            else:
                print('-', end = ""); sys.stdout.flush()


    # close database
    conn.close()
    print('done')
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))