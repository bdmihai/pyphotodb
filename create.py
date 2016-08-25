""" pyphotodb - create
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
    parser = argparse.ArgumentParser(prog='create.py')
    parser.add_argument('--rootPath', required=True, help='directory where the db shall be created')
    parser.add_argument('--noLogo', action='store_true', help='do not show logo')
    options = parser.parse_args(argv[1:])

    if (options.noLogo == False):
        print('PyPhoto Database Create Version 2.0.0')
        print('Copyright (C) B.D.Mihai. All rights reserved.')

    # prepare and check the root directory
    options.rootPath = os.path.normpath(options.rootPath)
    if (os.path.isdir(options.rootPath) == False):
        print('ERROR: Directory ' + options.rootPath + ' does not exist!')
        return 1
    if (os.access(options.rootPath, os.R_OK) == False):
        print('ERROR: Directory ' + options.rootPath + ' not readable!')
        return 1
    if (len(os.listdir(options.rootPath)) != 0):
        print('ERROR: Directory ' + options.rootPath + ' is not empty! Please provide a empty directory.')
        return 1

    # prepare directories
    print('Creating directories', end = "")
    os.mkdir(os.path.join(options.rootPath, 'bulk'));    print('.', end = ""); sys.stdout.flush()
    os.mkdir(os.path.join(options.rootPath, 'sort'));    print('.', end = ""); sys.stdout.flush()
    os.mkdir(os.path.join(options.rootPath, 'log'));     print('.', end = ""); sys.stdout.flush()
    os.mkdir(os.path.join(options.rootPath, 'backup'));  print('.', end = ""); sys.stdout.flush()
    os.mkdir(os.path.join(options.rootPath, 'cache'));   print('.', end = ""); sys.stdout.flush()
    print('done')

    # create logfile
    logging.basicConfig(filename = os.path.join(options.rootPath, 'log', datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S.create.log')), filemode = 'w', level = logging.DEBUG, format = '%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',)

    # create the database
    print('Creating database', end = "")
    conn = sqlite3.connect(os.path.join(options.rootPath, 'database.s3db')); c = conn.cursor()
    logging.info('Database: ' + os.path.join(options.rootPath, 'database.s3db'))
    cmd = '''CREATE TABLE [Photos] (
                [Id] INTEGER  PRIMARY KEY AUTOINCREMENT NOT NULL,
                [Name] VARCHAR(32)  UNIQUE NOT NULL,
                [Hash] VARCHAR(32)  NOT NULL,
                [Size] INTEGER  NOT NULL,
                [DateTime] TIMESTAMP  NOT NULL,
                [Make] VARCHAR(256)  NULL,
                [Model] VARCHAR(256)  NULL,
                [Software] VARCHAR(256)  NULL,
                [Width] INTEGER  NULL,
                [Height] INTEGER  NULL,
                [Orientation] VARCHAR(256)  NULL,
                [Latitude] FLOAT  NULL,
                [Longitude] FLOAT  NULL,
                [Altitude] FLOAT  NULL
            );'''
    c.execute(cmd); logging.info('Photos: ' + cmd); print('.', end=""); sys.stdout.flush()
    cmd = '''CREATE TABLE [Albums] (
                [Id] INTEGER  PRIMARY KEY AUTOINCREMENT NOT NULL,
                [Name] VARCHAR(1024)  NOT NULL,
                [PhotoId] INTEGER  NOT NULL
            );'''
    c.execute(cmd); logging.info('Albums: ' + cmd); print('.', end=""); sys.stdout.flush()
    cmd = '''CREATE TABLE [Tags] (
                [Id] INTEGER  PRIMARY KEY AUTOINCREMENT NOT NULL,
                [Name] VARCHAR(1024)  NOT NULL,
                [PhotoId] INTEGER  NOT NULL
            );'''
    c.execute(cmd); logging.info('Tags: ' + cmd); print('.', end=""); sys.stdout.flush()

    # close database
    conn.commit()
    conn.close()
    print('done')

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))