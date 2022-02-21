# KID drawer (DXF file generator) - Federico Cacciotti (c)2022

# import packages
import ezdxf
from ezdxf.addons import Importer
import numpy as np
from pathlib import Path
from os.path import exists

class Array():
    '''
	Parameters:
        input_dxf_path: string, path to the dxf pixel files
        n_pixels: int, number of pixel of the array
        positions: list of floats tuple, ordered list of (x,y) tuple positions of each pixel in microns
        rotations: list of floats, ordered list of rotation angle of each pixel in degrees
        mirror: list of chars, ordered list of chars of mirroring parameters, ex. 'x' means mirror with respect to the x axis
	See other function help for more info
	'''
    def __init__(self, input_dxf_path, n_pixels, position, rotation, mirror):
        self.input_dxf_path = input_dxf_path
        self.n_pixels = n_pixels
        self.position = position
        self.rotation = rotation
        self.mirror = mirror

        # check if files exist
        for i in range(self.n_pixels):
            file = self.input_dxf_path / 'pixel_{:d}.dxf'.format(i+1)
            if not exists(file):
                print("Error. '"+str(file)+"' does not exists.")
                return None

        # create the array dxf file
        array_dxf = ezdxf.new('R2018', setup=True)
        for i in range(self.n_pixels):
            # read pixel dxf files
            pixel_dxf = ezdxf.readfile(Path(self.input_dxf_path, 'pixel_{:d}.dxf'.format(i+1)))
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
                entity.transform(ezdxf.math.Matrix44.translate(self.position[i][0], self.position[i][1], 0.0))
            importer = Importer(pixel_dxf, array_dxf)
            importer.import_modelspace()
            importer.finalize()

        # save array dxf file
        array_dxf.saveas(self.input_dxf_path.parent / 'array.dxf')
