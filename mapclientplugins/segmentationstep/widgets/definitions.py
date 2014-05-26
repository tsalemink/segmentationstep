'''
MAP Client, a program to generate detailed musculoskeletal models for OpenSim.
    Copyright (C) 2012  University of Auckland
    
This file is part of MAP Client. (http://launchpad.net/mapclient)

    MAP Client is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    MAP Client is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with MAP Client.  If not, see <http://www.gnu.org/licenses/>..
'''
DEFAULT_NORMAL_ARROW_SIZE = 25.0
DEFAULT_GRAPHICS_SPHERE_SIZE = 10.0
DEFAULT_SEGMENTATION_POINT_SIZE = 2.0
GRAPHIC_LABEL_NAME = 'label_only'
IMAGE_PLANE_GRAPHIC_NAME = 'image_plane'
POINT_CLOUD_GRAPHIC_NAME = 'point_cloud'

class ViewMode(object):

    SEGMENT = 1
    PLANE_NORMAL = 2
    PLANE_ROTATION = 4


