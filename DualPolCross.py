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
    def __init__(self, index, h, l, d, w, capacitor_connector_w, capacitor_connector_h, capacitor_finger_number_1, capacitor_finger_width, capacitor_finger_gap):

        self.index = index
        self.h = h
        self.l = l
        self.d = d
        self.w = w
        self.capacitor_connector_w = capacitor_connector_w
        self.capacitor_connector_h = capacitor_connector_h
        self.capacitor_finger_number_1 = capacitor_finger_number_1
        self.capacitor_finger_width = capacitor_finger_width
        self.capacitor_finger_gap = capacitor_finger_gap
        # hidden parameters
        self.absorber_choke_d = 5.0
        self.absorber_choke_h = 3.0
        self.absorber_choke_w = 5.0
        self.absorber_choke_s = 7.0
        self.capacitor_size = (self.l*0.5+self.absorber_choke_d+2.0*self.absorber_choke_w+self.absorber_choke_s)*2.0
        self.capacitor_s = 15.0
        self.capacitor_finger_length = self.capacitor_size - 2.0*self.capacitor_finger_gap - 2.0*self.capacitor_connector_w

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
        self.__draw_center()
        self.__draw_index()
        self.__draw_capacitor_1()

        '''
        # merge all the polygons of the pixel layer and draw a single polyline
        pixel_pl = unary_union(self.__pixel_polygons__)
        points = pixel_pl.exterior.coords
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})
        '''



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
        def bulge(A, B):
            return 2.0/np.linalg.norm(A-B) * (np.linalg.norm(A) - np.sqrt(np.linalg.norm(A)**2.0-0.25*np.linalg.norm(A-B)**2.0))
        # quarter choke (bottom left)
        A = np.array([-self.absorber_choke_h*0.5, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h])
        B = np.array([-self.absorber_choke_h*0.5, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-self.absorber_choke_w])
        C = np.array([-self.l*0.5-self.absorber_choke_d-self.absorber_choke_w-self.absorber_choke_s, -self.h*0.5-self.w-self.absorber_choke_h-self.absorber_choke_w])
        D = np.array([-self.l*0.5-self.absorber_choke_d-self.absorber_choke_w, -self.h*0.5-self.w-self.absorber_choke_h-self.absorber_choke_w])
        E = np.array([-self.h*0.5, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_w])
        F = np.array([-self.h*0.5, -self.l*0.5])
        G = np.array([-self.h*0.5-self.w, -self.l*0.5])
        H = np.array([-self.h*0.5-self.w, -self.l*0.5-self.absorber_choke_d])
        I = np.array([-self.l*0.5-self.absorber_choke_d, -self.h*0.5-self.w-self.absorber_choke_h])
        J = np.array([-self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w, -self.h*0.5-self.w-self.absorber_choke_h])
        K = np.array([-self.absorber_choke_h*0.5-self.capacitor_connector_w, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w])
        L = np.array([-self.absorber_choke_h*0.5-self.capacitor_connector_w, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h])

        points = (A, (B[0], B[1], 0.0, 0.0, -bulge(B, C)), C, (D[0], D[1], 0.0, 0.0, bulge(D, E)), E, F, G , 
                  (H[0], H[1], 0.0, 0.0, -bulge(H, I)), I, (J[0], J[1], 0.0, 0.0, bulge(J, K)), K, L)
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})
        # quarter choke (bottom right)
        A = np.array([self.absorber_choke_h*0.5, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h])
        B = np.array([self.absorber_choke_h*0.5, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-self.absorber_choke_w])
        C = np.array([self.l*0.5+self.absorber_choke_d+self.absorber_choke_w+self.absorber_choke_s, -self.h*0.5-self.w-self.absorber_choke_h-self.absorber_choke_w])
        D = np.array([self.l*0.5+self.absorber_choke_d+self.absorber_choke_w, -self.h*0.5-self.w-self.absorber_choke_h-self.absorber_choke_w])
        E = np.array([self.h*0.5, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_w])
        F = np.array([self.h*0.5, -self.l*0.5])
        G = np.array([self.h*0.5+self.w, -self.l*0.5])
        H = np.array([self.h*0.5+self.w, -self.l*0.5-self.absorber_choke_d])
        I = np.array([self.l*0.5+self.absorber_choke_d, -self.h*0.5-self.w-self.absorber_choke_h])
        J = np.array([self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+2.0*self.absorber_choke_w, -self.h*0.5-self.w-self.absorber_choke_h])
        K = np.array([self.absorber_choke_h*0.5+self.capacitor_connector_w, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w])
        L = np.array([self.absorber_choke_h*0.5+self.capacitor_connector_w, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h])

        points = (A, (B[0], B[1], 0.0, 0.0, bulge(B, C)), C, (D[0], D[1], 0.0, 0.0, -bulge(D, E)), E, F, G , 
                  (H[0], H[1], 0.0, 0.0, bulge(H, I)), I, (J[0], J[1], 0.0, 0.0, -bulge(J, K)), K, L)
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})

        # half choke (top)
        A = np.array([-self.l*0.5, self.h*0.5])
        B = np.array([-self.l*0.5-self.absorber_choke_d-self.absorber_choke_w, self.h*0.5])
        C = np.array([self.l*0.5+self.absorber_choke_d+self.absorber_choke_w, self.h*0.5])
        D = np.array([self.l*0.5, self.h*0.5])
        E = np.array([self.l*0.5, self.h*0.5+self.w])
        F = np.array([self.l*0.5+self.absorber_choke_d, self.h*0.5+self.w])
        G = np.array([-self.l*0.5-self.absorber_choke_d, self.h*0.5+self.w])
        H = np.array([-self.l*0.5, self.h*0.5+self.w])
        points = (A, (B[0], B[1], 0.0, 0.0, -bulge(B, C)), C, D, E, (F[0], F[1], 0.0, 0.0, bulge(F, G)), G, H)
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})
        # quarter choke (top left)
        A = np.array([-self.l*0.5, -self.h*0.5])
        B = np.array([-self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-self.absorber_choke_w, -self.h*0.5])
        C = np.array([-self.absorber_choke_h*0.5, self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+self.absorber_choke_w])
        D = np.array([-self.absorber_choke_h*0.5, self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+2.0*self.absorber_choke_w+self.capacitor_connector_h])
        E = np.array([-self.absorber_choke_h*0.5-self.capacitor_connector_w, self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+2.0*self.absorber_choke_w+self.capacitor_connector_h])
        F = np.array([-self.absorber_choke_h*0.5-self.capacitor_connector_w, self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+2.0*self.absorber_choke_w])
        G = np.array([-self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w, -self.h*0.5-self.w])
        H = np.array([-self.l*0.5, -self.h*0.5-self.w])
        points = (A, (B[0], B[1], 0.0, 0.0, -bulge(B, C)), C, D, E, (F[0], F[1], 0.0, 0.0, bulge(F, G)), G, H)
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})
        # quarter choke (top right)
        A = np.array([self.l*0.5, -self.h*0.5])
        B = np.array([self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+self.absorber_choke_w, -self.h*0.5])
        C = np.array([self.absorber_choke_h*0.5, self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+self.absorber_choke_w])
        D = np.array([self.absorber_choke_h*0.5, self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+2.0*self.absorber_choke_w+self.capacitor_connector_h])
        E = np.array([self.absorber_choke_h*0.5+self.capacitor_connector_w, self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+2.0*self.absorber_choke_w+self.capacitor_connector_h])
        F = np.array([self.absorber_choke_h*0.5+self.capacitor_connector_w, self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+2.0*self.absorber_choke_w])
        G = np.array([self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+2.0*self.absorber_choke_w, -self.h*0.5-self.w])
        H = np.array([self.l*0.5, -self.h*0.5-self.w])
        points = (A, (B[0], B[1], 0.0, 0.0, bulge(B, C)), C, D, E, (F[0], F[1], 0.0, 0.0, -bulge(F, G)), G, H)
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})
    
    
    # draws the interdigital capacitor
    def __draw_capacitor_1(self):
        polygons = []

        finger_number_int = int(self.capacitor_finger_number_1)

        # draw fingers
        y_shift = -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_s
        x_shift = -self.capacitor_size*0.5+self.capacitor_connector_w
        for i in range(finger_number_int):
            corner0 = (((i+1)%2)*self.capacitor_finger_gap + self.capacitor_connector_w + x_shift, -i*(self.capacitor_finger_width+self.capacitor_finger_gap) + y_shift)
            y_size = self.capacitor_finger_width
            x_size = self.capacitor_finger_length
            self.msp.add_lwpolyline(fc.draw_rectangle_corner_dimensions_points(corner0, x_size, y_size), close=True, dxfattribs={"layer": self.pixel_layer_name})
            #polygons.append(fc.draw_rectangle_corner_dimensions(corner0, x_size, y_size))

        # connectors
        A = np.array([-self.absorber_choke_h*0.5, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h])
        B = np.array([-self.capacitor_size*0.5, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h])
        C = np.array([-self.capacitor_size*0.5, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_s])
        D = np.array([-self.capacitor_size*0.5+self.capacitor_connector_w, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_s])
        E = np.array([-self.capacitor_size*0.5+self.capacitor_connector_w, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_connector_w])
        F = np.array([-self.absorber_choke_h*0.5, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_connector_w])
        points = (A, B, C, D, E, F)
        #polygons.append(Polygon(points))
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})


        # merge all the polygons of the pixel layer and draw a single polyline
        #points = unary_union(polygons).exterior.coords
        #self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})
        '''
        # pinky finger
        if self.capacitor_finger_number_1-finger_number_int != 0.0:
            pinky_length = self.capacitor_finger_length*(self.capacitor_finger_number-finger_number_int)
            corner0 = (-self.capacitor_finger_gap-self.capacitor_finger_width, self.line_width)
            x_size = self.capacitor_finger_width
            y_size = pinky_length
            self.__pixel_polygons__.append(fc.draw_rectangle_corner_dimensions(corner0, x_size, y_size))

        # draw the two horizontal lines
        # upper line
        corner0 = (0.0, self.vertical_size-self.line_width)
        x_size = finger_number_int*self.capacitor_finger_width + (finger_number_int-1)*self.capacitor_finger_gap
        y_size = self.line_width
        self.__pixel_polygons__.append(fc.draw_rectangle_corner_dimensions(corner0, x_size, y_size))
        # lower line
        if self.capacitor_finger_number-finger_number_int != 0.0:
            corner0 = (-self.capacitor_finger_gap-self.capacitor_finger_width, 0.0)
            x_size = (finger_number_int+1)*self.capacitor_finger_width + finger_number_int*self.capacitor_finger_gap
            y_size = self.line_width
            self.__pixel_polygons__.append(fc.draw_rectangle_corner_dimensions(corner0, x_size, y_size))
        else:
            corner0 = (0.0, 0.0)
            self.__pixel_polygons__.append(fc.draw_rectangle_corner_dimensions(corner0, x_size, y_size))
        '''
    
    # draws a cross over the absorber to find its center
    def __draw_center(self):
        # draw the diagonals to find the center
        points = ((-self.l*0.5, -self.l*0.5), (self.l*0.5, self.l*0.5))
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.center_layer_name})
        points = ((-self.l*0.5, self.l*0.5), (self.l*0.5, -self.l*0.5))
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.center_layer_name})


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
