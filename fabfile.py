#!/usr/bin/env python
"""
This fabfile will allow us to style, render and deploy our map tiles for the redistricting project.
"""

import sys
import warnings

from fabric.api import local

try:
    exec(open('project_dirs.py'))
except IOError:
    warnings.warn('Using default variables - please create a project_dirs.py file')
    MAPS_LIST = ['vikings_bill_house']
    MAPBOX_PROJECTS_DIRECTORY = '/Users/kevin/Documents/MapBox/project/'
    MAPBOX_EXPORT_DIRECTORY = '/Users/kevin/Documents/MapBox/export/'
    PROJECT_DIRECTORY = '/Users/kevin/dropbox/projects/vikings_bill/'
    S3_DIRECTORY_S3CMD = 's3://schaul/maps/vikings_bill/house/'
    S3_DIRECTORY = 'schaul/maps/vikings_bill/house/'

# #
# When making changes, update this and in map/data/{MAPS_LIST}.json
VERSION = '1.0'

# #
# Functions
def deploy_all():
    """
    Copies the .mbtils file from exported MapBox projects, runs mb-util, deploys to s3
    Use this when all maps have changed.
    """

    for map in MAPS_LIST:
        copy_map_dirs(map)
        extract_tiles(map)
        deploy_map(map)
        deploy_json(map)

def setup_deploy_map(map):
    """
    Calls copy_map_dirs, extract_tiles, deploy_map and deploy_json.
    """
    copy_map_dirs(map)
    extract_tiles(map)
    deploy_map(map)
    deploy_json(map)

def deploy_json(map):
    """
    Sends json file to s3
    """
    command = 's3cmd put -P ' + PROJECT_DIRECTORY + map + '.json ' + S3_DIRECTORY_S3CMD
    local(command)

def copy_map_dirs(map):
    """
    Sets up dirs for map, copies .mbtiles file
    """
    print 'Making map directory: ' + map
    command = 'mkdir -p tiles_' + map
    local(command)

    print 'Copying .mbtiles file: ' + map
    command = 'cp ' + MAPBOX_EXPORT_DIRECTORY + map + '.mbtiles ' + PROJECT_DIRECTORY + 'tiles_' + map
    local(command)

def extract_tiles(map):
    """
    Removes previously rendered tiles, then runs mb-util on the .mbtiles file.
    """
    print 'Removing previously rendered tyles for map: ' + map
    command = 'rm -Rf ' + PROJECT_DIRECTORY + 'tiles_' + map + '/rendered_tiles'
    local(command)

    print 'Running mb-util for map: ' + map
    command = 'mb-util ' + PROJECT_DIRECTORY + 'tiles_' + map + '/' + map + '.mbtiles rendered_tiles'
    local(command)

    print 'Moving json file into rendered_tiles'
    command = 'mv ' + PROJECT_DIRECTORY + map + '.json ' + 'rendered_tiles/'

    print 'Moving rendered_tiles into correct directory'
    command = 'mv ' + PROJECT_DIRECTORY + 'rendered_tiles ' + PROJECT_DIRECTORY + 'tiles_' + map + '/'
    local(command)

    print 'Fixing version number'
    command = 'mv ' + PROJECT_DIRECTORY + 'tiles_' + map + '/rendered_tiles/1.0.0 ' + PROJECT_DIRECTORY + 'tiles_' + map + '/rendered_tiles/' + VERSION
    local(command)

def deploy_map(map):
    """
    Deploys the rendered tiles to s3.
    """

    print 'Deploying map: ' + map
    command = 'ivs3 --concurrency 32 -P ' + PROJECT_DIRECTORY + 'tiles_' + map + '/rendered_tiles/ ' + S3_DIRECTORY
    local(command)

