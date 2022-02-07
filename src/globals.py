"""
File to store various program-wide constants
"""

import os
import bpy

basedir = bpy.path.abspath("//")

OUTPUT_FOLDER = os.path.join(basedir, "out")
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

RENDER_FRAME = 1 #The frame at which the render is done. Used for motion blurring