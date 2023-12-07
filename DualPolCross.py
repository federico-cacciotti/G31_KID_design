# KID drawer (DXF file generator) - Federico Cacciotti (c)2022

#

# import packages
import ezdxf
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing import Frontend, RenderContext
import numpy as np
import os
from pathlib import Path
from matplotlib import pyplot as plt
from shapely.geometry import Polygon
from shapely.ops import unary_union
from . import functions as fc


# units: micron
class DualPolCross():
    def __init__(self, index, h, l, d, w, capacitor_connector_w, capacitor_connector_h):

        self.index = index
        self.h = h
        self.l = l
        self.d = d
        self.w = w
        self.capacitor_connector_w = capacitor_connector_w
        self.capacitor_connector_h = capacitor_connector_h

        self.info_string = ("units: microns\n"
                                "index:                       {:d}\n"
                                "h:                           {:.2f}\n"
                                "l:                           {:.2f}\n"
                                "d:                           {:.2f}\n"
                                "w:                           {:.2f}\n"
                                "\n".format(self.index,
                                            self.h,
                                            self.l,
                                            self.d,
                                            self.w))
        
        # Create a new DXF R2018 drawing
        self.dxf = ezdxf.new('R2018', setup=True)
        # layer names
        self.pixel_layer_name = "PIXEL"
        self.center_layer_name = "CENTER"
        self.pixel_area_layer_name = "PIXEL_AREA"
        self.absorber_area_layer_name = "ABSORBER_AREA"
        self.index_layer_name = "INDEX"
        # layer colors - AutoCAD Color Index - table on http://gohtx.com/acadcolors.php
        self.pixel_layer_color = 255
        self.pixel_area_layer_color = 140
        self.absorber_area_layer_color = 150
        self.center_layer_color = 120
        self.index_layer_color = 254

        # adds layers
        self.dxf.layers.add(name=self.pixel_layer_name, color=self.pixel_layer_color)
        self.dxf.layers.add(name=self.center_layer_name, color=self.center_layer_color)
        self.dxf.layers.add(name=self.pixel_area_layer_name, color=self.pixel_area_layer_color)
        self.dxf.layers.add(name=self.absorber_area_layer_name, color=self.absorber_area_layer_color)
        self.dxf.layers.add(name=self.index_layer_name, color=self.index_layer_color)

        # adds a modelspace
        self.msp = self.dxf.modelspace()

        # list of all the polygons that draw the whole pixel
        self.__pixel_polygons__ = []

        # draw the pixel
        self.__draw_absorber()
        self.__draw_capacitor_connetor()
        self.__draw_index()






    def __draw_absorber(self):
        # vertical polarization absorber
        points = ((-self.h*0.5-self.w, -self.l*0.5),
                    (-self.h*0.5-self.w, self.l*0.5),
                    (self.h*0.5+self.w, self.l*0.5),
                    (self.h*0.5+self.w, -self.l*0.5),
                    (self.h*0.5, -self.l*0.5),
                    (self.h*0.5, self.l*0.5-self.w),
                    (-self.h*0.5, self.l*0.5-self.w),
                    (-self.h*0.5, -self.l*0.5))
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})

        # left horizontal polarization absorber
        points = ((-self.l*0.5, -self.h*0.5-self.w),
                  (-self.d-self.h*0.5-self.w, -self.h*0.5-self.w),
                  (-self.d-self.h*0.5-self.w, self.h*0.5+self.w),
                  (-self.l*0.5, self.h*0.5+self.w),
                  (-self.l*0.5, self.h*0.5),
                  (-self.d-self.h*0.5-2.0*self.w, self.h*0.5),
                  (-self.d-self.h*0.5-2.0*self.w, -self.h*0.5),
                  (-self.l*0.5, -self.h*0.5))
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})

        # right horizontal polarization absorber
        points = ((self.l*0.5, -self.h*0.5-self.w),
                  (self.d+self.h*0.5+self.w, -self.h*0.5-self.w),
                  (self.d+self.h*0.5+self.w, self.h*0.5+self.w),
                  (self.l*0.5, self.h*0.5+self.w),
                  (self.l*0.5, self.h*0.5),
                  (self.d+self.h*0.5+2.0*self.w, self.h*0.5),
                  (self.d+self.h*0.5+2.0*self.w, -self.h*0.5),
                  (self.l*0.5, -self.h*0.5))
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})


    # draws the capacitor connectors
    def __draw_capacitor_connetor(self):
        # vertical absorber connector
        internal_radius = np.sqrt((self.h*0.5+self.w)**2.0 + (0.5*self.l)**2.0)
        self.msp.add_arc(radius=internal_radius, center=(0.0, 0.0), start_angle=180.0, end_angle=270.0, dxfattribs={"layer": self.pixel_layer_name})



    # draws the text index on the absorber
    def __draw_index(self):
        position = (0.0, 0.0)
        height = 0.35*self.l
        text = str(self.index)
        self.msp.add_text(text, dxfattribs={'height': height, 'layer': self.index_layer_name}).set_pos(position, align='CENTER')

    
    # prints on screen all the parameters
    def print_info(self):
        '''
		This function prints on screen all the design parameters and 
        information

        Returns
        -------
        None.

        '''
        print(self.info_string)

    # saves a dxf file of the pixel
    def save_dxf(self, filename):
        '''
        This function saves a .dxf file of a pixel design.
        The drawing has many layers:
            - PIXEL: the actual layer where the KID is shown
            - PIXEL_AREA: a layer where a rectangle encloses the whole pixel
            - ABSORBER_AREA: a layer where a square encloses the absorber 
                section of the KID
            - CENTER: a layer where the two diagonals of the ABSORBER_AREA 
                square are shown
            - INDEX: a layer where the self.index value of the pixel is shown
        The output drawing has the absorber centered to the origin.

        Parameters
        ----------
        filename : string
            The path and name of the script file (ex. 'a/b/pixel0.scr').

        Returns
        -------
        None.

        '''
        # make dxf directory
        filename = Path(filename)
        if not os.path.exists(filename.parent):
            os.makedirs(filename.parent)

        self.dxf.saveas(filename)

    # saves the figure of a pixel
    def saveFig(self, filename, dpi=250):
        '''
        This function saves a figure of the array design.
        
    	Parameters
        ----------
        filename : string
            Output path and filename of the figure.
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
        Frontend(RenderContext(self.dxf), backend).draw_layout(self.msp)
        fig.savefig(filename, dpi=dpi)
        plt.show()
