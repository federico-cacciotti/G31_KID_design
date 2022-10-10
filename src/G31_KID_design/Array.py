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
    def __init__(self, input_dxf_path, n_pixels, x_pos, y_pos, rotation=None, mirror=None, output_dxf='array.dxf', feedline_dxf=None, focal_plane_dxf=None, wafer_limits=None):
        '''
        This class is used for the generation of an array design.

        Parameters
        ----------
        input_dxf_path : string
            Path to the dxf pixel files.
        n_pixels : int
            Number of pixel of the array.
        x_pos : list of floats
            Ordered list of x positions of each pixel in microns.
        y_pos : list of floats
            Ordered list of y positions of each pixel in microns.
        rotation : list of floats, optional
            Ordered list of rotation angle of each pixel in degrees. The
            default is None.
        mirror : list of chars, optional
            ordered list of chars ('x', 'y' or None) of mirroring parameters, 
            ex. 'x' means mirror with respect to the x axis.  The default is 
            None.
        output_dxf : string, optional
            Output filename. The default is 'array.dxf'.
        feedline_dxf : string, optional
            The path to a .dxf file with the feedline drawing. The drawing must
            be placed on the 'FEEDLINE' layer. The default is None.
        focal_plane_dxf : string, optional
            The path to a .dxf file with the focal plane useful area drawing. 
            The drawing must be placed on the 'FOCAL_PLANE' layer. The default 
            is None.
        wafer_limits : string, optional
            The path to a .dxf file with the wafer perimeter drawing. 
            The drawing must be placed on the 'WAFER_LIMIT' layer. The default 
            is None.

        Returns
        -------
        None.

        '''
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
        
        # import the feedline drawing if given
        if feedline_dxf != None:
            feedline = ezdxf.readfile(feedline_dxf)
            importer = Importer(feedline, self.array_dxf)
            importer.import_modelspace()
            importer.finalize()
            
        # import the focal plane useful area drawing if given
        if focal_plane_dxf != None:
            focal_plane = ezdxf.readfile(focal_plane_dxf)
            importer = Importer(focal_plane, self.array_dxf)
            importer.import_modelspace()
            importer.finalize()
            
        # import the wafer limit perimeter
        if wafer_limits != None:
            wafer = ezdxf.readfile(wafer_limits)
            importer = Importer(wafer, self.array_dxf)
            importer.import_modelspace()
            importer.finalize()
        
        for i in range(self.n_pixels):
            # read pixel dxf files
            pixel_dxf = ezdxf.readfile(self.input_dxf_path / 'pixel_{:d}.dxf'.format(i+1))
            for entity in pixel_dxf.modelspace():
                # the textual index should be translated only
                # type(entity) == ezdxf.entities.text.Text return True if the
                # entity is the textual index
                if not type(entity) == ezdxf.entities.text.Text:
                    # mirroring
                    if self.mirror != None:
                        if self.mirror[i] == 'x':
                            entity.transform(ezdxf.math.Matrix44.scale(sx=-1, sy=1, sz=1))
                        if self.mirror[i] == 'y':
                            entity.transform(ezdxf.math.Matrix44.scale(sx=1, sy=-1, sz=1))
                    # rotation
                    if self.rotation != None:
                        entity.transform(ezdxf.math.Matrix44.z_rotate(np.radians(self.rotation[i])))
                # translation
                entity.transform(ezdxf.math.Matrix44.translate(self.x_pos[i], self.y_pos[i], 0.0))
            importer = Importer(pixel_dxf, self.array_dxf)
            importer.import_modelspace()
            importer.finalize()

        # save array dxf file
        self.array_dxf.saveas(self.input_dxf_path.parent / output_dxf)

    # saves the figure of the array
    def saveFig(self, filename='array.png', dpi=250):
        '''
        This function saves a figure of the array design.

        Parameters
        ----------
        filename : string, optional
            Output path and filename of the figure. The default is 'array.png'.
        dpi : int, optional
            Dpi of the figure. The default is 250.

        Returns
        -------
        None.

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
