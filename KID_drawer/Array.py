# KID drawer (DXF file generator) - Federico Cacciotti (c)2022

# importa packages
import ezdxf
from ezdxf.addons import Importer
import numpy as np

class Array():
    '''
	Parameters:
		n_pixels: int, number of pixel of the array
        positions: list of floats, ordered list of (x,y) tuple positions of each pixel in microns
        rotations: list of floats, ordered list of rotation angle of each pixel in degrees
	See other function help for more info
	'''
    def __init__(self, input_dxf_path, n_pixels, positions, rotations):
        self.input_dxf_path = input_dxf_path
        self.n_pixels = n_pixels
        self.positions = positions
        self.rotations = rotations
