# KID drawer (DXF file generator) - Federico Cacciotti (c)2022

# import packages
import ezdxf
from ezdxf.addons import Importer
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing import Frontend, RenderContext
import numpy as np
from pathlib import Path
from os.path import exists
from matplotlib import pyplot as plt
import os

class Array():
    '''
	Parameters:
        input_dxf_path: string, path to the dxf pixel files
        n_pixels: int, number of pixel of the array
        x_pos: list of floats, ordered list of x positions of each pixel in microns
        y_pos: list of floats, ordered list of y positions of each pixel in microns
        rotations: list of floats, ordered list of rotation angle of each pixel in degrees
        mirror: list of chars, ordered list of chars of mirroring parameters, ex. 'x' means mirror with respect to the x axis
	See other function help for more info
	'''
    def __init__(self, input_dxf_path, n_pixels, x_pos, y_pos, rotation, mirror):
        self.input_dxf_path = Path(input_dxf_path)
        self.n_pixels = n_pixels
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.rotation = rotation
        self.mirror = mirror

        # check if files exist
        for i in range(self.n_pixels):
            file = Path(self.input_dxf_path, 'pixel_{:d}.dxf'.format(i+1))
            if not exists(file):
                print("Error. '"+str(file)+"' does not exists.")
                return None

        # create the array dxf file
        self.array_dxf = ezdxf.new('R2018', setup=True)
        for i in range(self.n_pixels):
            # read pixel dxf files
            pixel_dxf = ezdxf.readfile(self.input_dxf_path / 'pixel_{:d}.dxf'.format(i+1))
            for entity in pixel_dxf.modelspace():
                # the textual index should be translated only
                # type(entity) == ezdxf.entities.text.Text return True if the
                # entity is the textual index
                if not type(entity) == ezdxf.entities.text.Text:
                    # mirroring
                    if self.mirror[i] == 'x':
                        entity.transform(ezdxf.math.Matrix44.scale(sx=-1, sy=1, sz=1))
                    if self.mirror[i] == 'y':
                        entity.transform(ezdxf.math.Matrix44.scale(sx=1, sy=-1, sz=1))
                    # rotation
                    if self.rotation[i] != 0.0:
                        entity.transform(ezdxf.math.Matrix44.z_rotate(np.radians(self.rotation[i])))
                # translation
                entity.transform(ezdxf.math.Matrix44.translate(self.x_pos[i], self.y_pos[i], 0.0))
            importer = Importer(pixel_dxf, self.array_dxf)
            importer.import_modelspace()
            importer.finalize()

        # save array dxf file
        self.array_dxf.saveas(self.input_dxf_path.parent / 'array.dxf')

    # saves the figure of the array
    def saveFig(self, filename, dpi=150):
        '''
        Save a figure of the drawing
    	Parameters:
            filename: string, output path and filename of the figure
            dpi: int (optional), dpi of the figure, default value: 150
        '''
        # check if the output directory exists
        filename = Path(filename)
        if not os.path.exists(filename.parent):
            os.makedirs(filename.parent)

        fig = plt.figure()
        ax = fig.add_axes([0, 0, 1, 1])
        backend = MatplotlibBackend(ax)
        Frontend(RenderContext(self.array_dxf), backend).draw_layout(self.array_dxf.modelspace())
        fig.savefig(filename, dpi=dpi)
