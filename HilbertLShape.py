# KID drawer (DXF file generator) - Federico Cacciotti (c)2022
#     ____________________________________
#    |____________________________________|
#    |
#    |_____________     _________      _________
#    |   |         |   |         |    |         |
#    | | | |   ____|   |____     |____|     ____|
#    | | | |  |             |              |
#    | | | |  |     ___     |     ____     |____
#    | | | |  |    |   |    |    |    |         |
#    | | | |  |____|   |____|    |    |_________|
#    | | | |                     |
#  | | | | |   ____     ____     |     _________
#  | | | | |  |    |   |    |    |    |         |
#  | | | | |  |    |___|    |    |____|     ____|
#  | | | | |  |             |              |
#  | | | | |  |____     ____|     ____     |____
#  | | | | |       |   |         |    |         |
#  |___|___|_______|   |_________|    |_________|
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


# units: micron
class HilbertLShape():
    def __init__(self, index, vertical_size, line_width, coupling_capacitor_length, coupling_capacitor_width,
                 coupling_connector_width, coupling_capacitor_y_offset, capacitor_finger_number,
                 capacitor_finger_gap, capacitor_finger_width, hilbert_order, absorber_separation):
        '''
        This class generates a pixel design like the image below:
                 ____________________________________       
                |____________________________________|      
                |                                           
                |_____________     _________      _________ 
                |   |         |   |         |    |         |
                | | | |   ____|   |____     |____|     ____|
                | | | |  |             |              |     
                | | | |  |     ___     |     ____     |____ 
                | | | |  |    |   |    |    |    |         |
                | | | |  |____|   |____|    |    |_________|
                | | | |                     |               
              | | | | |   ____     ____     |     _________ 
              | | | | |  |    |   |    |    |    |         |
              | | | | |  |    |___|    |    |____|     ____|
              | | | | |  |             |              |     
              | | | | |  |____     ____|     ____     |____ 
              | | | | |       |   |         |    |         |
              |___|___|_______|   |_________|    |_________|

        Parameters
        ----------
        index : int
            The index number of the pixel.
        vertical_size : float
            Edge size of the absorber in microns.
        line_width : float
            Width of the conductive path in microns.
        coupling_capacitor_length : float
            Length of the coupling capacitor in microns.
        coupling_capacitor_width : float
            Width of the coupling capacitor in microns.
        coupling_connector_width : float
            Width of the conductive segment that goes from the pixel to the 
            coupling capacitor in microns.
        coupling_capacitor_y_offset : float
            Vertical separation between the pixel and the coupling capacitor
            in microns.
        capacitor_finger_number : float
            Number of fingers of the interdigital capacitor with decimal digits
            meaning an extra finger of variable length.
        capacitor_finger_gap : float
            Gap between interdigitated fingers in microns.
        capacitor_finger_width : float
            Width of the interdigitated fingers in microns.
        hilbert_order : int
            Hilbert order of the absorber (it is reccommended to not exceed 
            the 7th order for computational reasons, but you can do the f*ck 
            you want though :) ).
        absorber_separation : float
            Horizontal separation of the absorber from the capacitor in 
            microns.

        Returns
        -------
        None.

        '''
        self.index = index
        self.vertical_size = vertical_size
        self.line_width = line_width
        self.coupling_capacitor_length = coupling_capacitor_length
        self.coupling_capacitor_width = coupling_capacitor_width
        self.coupling_connector_width = coupling_connector_width
        self.coupling_capacitor_y_offset = coupling_capacitor_y_offset
        self.capacitor_finger_number = capacitor_finger_number
        self.capacitor_finger_gap = capacitor_finger_gap
        self.capacitor_finger_length = self.vertical_size-2*self.line_width-self.capacitor_finger_gap
        self.capacitor_finger_width = capacitor_finger_width
        self.hilbert_order = hilbert_order
        self.absorber_separation = absorber_separation

        self.info_string = ("units: microns\n"
                            "index:                       {:d}\n"
                            "vertical_size:               {:.2f}\n"
                            "line_width:                  {:.2f}\n"
                            "coupling_capacitor_length:   {:.2f}\n"
                            "coupling_capacitor_width:    {:.2f}\n"
                            "coupling_connector_width:    {:.2f}\n"
                            "coupling_capacitor_y_offset: {:.2f}\n"
                            "capacitor_finger_number:     {:.2f}\n"
                            "capacitor_finger_gap:        {:.2f}\n"
                            "capacitor_finger_length:     {:.2f}\n"
                            "capacitor_finger_width:      {:.2f}\n"
                            "hilbert_order:               {:d}\n"
                            "absorber_separation:         {:.2f}\n"
                            "\n".format(self.index,
                                        self.vertical_size,
                                        self.line_width,
                                        self.coupling_capacitor_length,
                                        self.coupling_capacitor_width,
                                        self.coupling_connector_width,
                                        self.coupling_capacitor_y_offset,
                                        self.capacitor_finger_number,
                                        self.capacitor_finger_gap,
                                        self.capacitor_finger_length,
                                        self.capacitor_finger_width,
                                        self.hilbert_order,
                                        self.absorber_separation))

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

    # draws a lwpolyline from a list of points
    def __draw_polyline(self, points, layer):
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": layer})

    # adds a rectangle from opposite corners coordinates as a lwpolyline
    def __draw_rectangle_corner_dimensions(self, corner0, x_size, y_size):
        points =   ( corner0,
                    (corner0[0]+x_size, corner0[1]),
                    (corner0[0]+x_size, corner0[1]+y_size),
                    (corner0[0], corner0[1]+y_size))
        return Polygon(points)
        #self.msp.add_lwpolyline(points, close=False, dxfattribs={"layer": layer})

    # adds a rectangle from the center coordinates and dimensions as a lwpolyline
    def __draw_rectangle_center_dimensions(self, center, x_size, y_size):
        points =   ((center[0]-0.5*x_size, center[1]-0.5*y_size),
                    (center[0]+0.5*x_size, center[1]-0.5*y_size),
                    (center[0]+0.5*x_size, center[1]+0.5*y_size),
                    (center[0]-0.5*x_size, center[1]+0.5*y_size))
        return Polygon(points)
        #self.msp.add_lwpolyline(points, close=False, dxfattribs={"layer": layer})

    # draws the single coupling capacitor
    def __draw_coupling_capacitor(self):
        corner0 = (0, self.vertical_size+self.coupling_capacitor_y_offset)
        x_size = self.coupling_capacitor_length
        y_size = self.coupling_capacitor_width
        self.__pixel_polygons__.append(self.__draw_rectangle_corner_dimensions(corner0, x_size, y_size))

    # draws the interdigital capacitor
    def __draw_capacitor(self):
        finger_number_int = int(self.capacitor_finger_number)

        # draw fingers
        for i in range(finger_number_int):
            corner0 = (i*(self.capacitor_finger_width+self.capacitor_finger_gap), ((i+1)%2)*self.capacitor_finger_gap + self.line_width)
            x_size = self.capacitor_finger_width
            y_size = self.capacitor_finger_length
            self.__pixel_polygons__.append(self.__draw_rectangle_corner_dimensions(corner0, x_size, y_size))

        # pinky finger
        if self.capacitor_finger_number-finger_number_int != 0.0:
            pinky_length = self.capacitor_finger_length*(self.capacitor_finger_number-finger_number_int)
            corner0 = (-self.capacitor_finger_gap-self.capacitor_finger_width, self.line_width)
            x_size = self.capacitor_finger_width
            y_size = pinky_length
            self.__pixel_polygons__.append(self.__draw_rectangle_corner_dimensions(corner0, x_size, y_size))

        # draw the two horizontal lines
        # upper line
        corner0 = (0.0, self.vertical_size-self.line_width)
        x_size = finger_number_int*self.capacitor_finger_width + (finger_number_int-1)*self.capacitor_finger_gap
        y_size = self.line_width
        self.__pixel_polygons__.append(self.__draw_rectangle_corner_dimensions(corner0, x_size, y_size))
        # lower line
        if self.capacitor_finger_number-finger_number_int != 0.0:
            corner0 = (-self.capacitor_finger_gap-self.capacitor_finger_width, 0.0)
            x_size = (finger_number_int+1)*self.capacitor_finger_width + finger_number_int*self.capacitor_finger_gap
            y_size = self.line_width
            self.__pixel_polygons__.append(self.__draw_rectangle_corner_dimensions(corner0, x_size, y_size))
        else:
            corner0 = (0.0, 0.0)
            self.__pixel_polygons__.append(self.__draw_rectangle_corner_dimensions(corner0, x_size, y_size))

    # draws the hilbert shaped absorber
    def __draw_absorber(self):
        axiom = "X"
        X_rule = "-YF+XFX+FY-"
        Y_rule = "+XF-YFY-FX+"
        for i in range(self.hilbert_order):
            new_axiom = ""
            for word in axiom:
                if word == "X":
                    new_axiom += X_rule
                elif word == "Y":
                    new_axiom += Y_rule
                else:
                    new_axiom += word
            axiom = new_axiom
        axiom = axiom.replace("X", "")
        axiom = axiom.replace("Y", "")
        axiom = axiom.replace("+-", "")
        axiom = axiom.replace("-+", "")

        points = []

        # add an initial horizontal offset to the hilbert pattern
        points.append([0.5*self.line_width, 0.0])
        L_el = (self.vertical_size-self.line_width)/(2.0**self.hilbert_order-1)
        step = [0, L_el]
        for word in axiom:
            if word == "-":     # turn right
                new_step = [step[1], -step[0]]
                step = new_step
            elif word == "+":   # turn left
                new_step = [-step[1], step[0]]
                step = new_step
            elif word == "F":
                points.append(step)
        # add a final horizontal offset to the hilbert pattern
        points.append([-0.5*self.line_width, 0.0])

        # draw the midline
        x0 = self.absorber_separation+int(self.capacitor_finger_number)*self.capacitor_finger_width+int(self.capacitor_finger_number-1)*self.capacitor_finger_gap
        y0 = 0.5*self.line_width
        starting_point = [x0, y0]

        for point in points:
            center = (0.5*(2*starting_point[0]+point[0]), 0.5*(2*starting_point[1]+point[1]))
            x_size = np.abs(point[0])+self.line_width
            y_size = np.abs(point[1])+self.line_width
            self.__pixel_polygons__.append(self.__draw_rectangle_center_dimensions(center, x_size, y_size))
            starting_point = [starting_point[0]+point[0], starting_point[1]+point[1]]

    # draws connection lines between components
    def __connect_components(self):
        # coupling capacitor connector
        corner0 = (0.0, self.vertical_size)
        x_size = self.coupling_connector_width
        y_size = self.coupling_capacitor_y_offset
        self.__pixel_polygons__.append(self.__draw_rectangle_corner_dimensions(corner0, x_size, y_size))

        # absorber connectors
        x0 = int(self.capacitor_finger_number)*self.capacitor_finger_width+int(self.capacitor_finger_number-1)*self.capacitor_finger_gap
        corner0 = (x0, 0.0)
        x_size = self.absorber_separation
        y_size = self.line_width
        self.__pixel_polygons__.append(self.__draw_rectangle_corner_dimensions(corner0, x_size, y_size))
        corner0 = (x0, self.vertical_size-self.line_width)
        self.__pixel_polygons__.append(self.__draw_rectangle_corner_dimensions(corner0, x_size, y_size))

    # draws a cross over the absorber to find its center
    def __draw_center(self):
        # draw the diagonals to find the center
        x0 = self.absorber_separation+int(self.capacitor_finger_number)*self.capacitor_finger_width+int(self.capacitor_finger_number-1)*self.capacitor_finger_gap
        points = ((x0, 0.0), (x0+self.vertical_size, self.vertical_size))
        self.__draw_polyline(points, self.center_layer_name)
        points = ((x0, self.vertical_size), (x0+self.vertical_size, 0.0))
        self.__draw_polyline(points, self.center_layer_name)

    # draws a box over the whole pixel
    def __draw_pixel_area(self):
        cor0 = [0.0, 0.0]
        cor1 = [0.0, 0.0]

        finger_number_int = int(self.capacitor_finger_number)
        cor1[0] = finger_number_int*self.capacitor_finger_width+(finger_number_int-1)*self.capacitor_finger_gap+self.absorber_separation+self.vertical_size
        cor1[1] = self.vertical_size+self.coupling_capacitor_width+self.coupling_capacitor_y_offset
        x_size = cor1[0]-cor0[0]

        # check if the copuling length is longer than the pixel size
        if self.coupling_capacitor_length > x_size:
            cor1[0] = self.coupling_capacitor_length
            x_size = cor1[0]-cor0[0]

        # check if the extra finger is present
        if int(self.capacitor_finger_number)-self.capacitor_finger_number != 0:
            cor0[0] = -self.capacitor_finger_gap-self.capacitor_finger_width
            x_size = cor1[0]-cor0[0]

        y_size = cor1[1]-cor0[1]
        self.__draw_polyline(self.__draw_rectangle_corner_dimensions(cor0, x_size, y_size).exterior.coords, self.pixel_area_layer_name)

    # draws a box over the absorber
    def __draw_absorber_area(self):
        corner0 = (self.absorber_separation+int(self.capacitor_finger_number)*self.capacitor_finger_width+int(self.capacitor_finger_number-1)*self.capacitor_finger_gap, 0.0)
        x_size = self.vertical_size
        y_size = self.vertical_size
        self.__draw_polyline(self.__draw_rectangle_corner_dimensions(corner0, x_size, y_size).exterior.coords, self.absorber_area_layer_name)

    # draws the text index on the absorber
    def __draw_index(self):
        position = (self.absorber_separation+int(self.capacitor_finger_number)*self.capacitor_finger_width+int(self.capacitor_finger_number-1)*self.capacitor_finger_gap, 0.0)
        height = 0.35*self.vertical_size
        text = str(self.index)
        self.msp.add_text(text, dxfattribs={'height': height, 'layer': self.index_layer_name}).set_pos(position, align='LEFT')

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

        # draw pixel
        self.__draw_coupling_capacitor()
        self.__draw_capacitor()
        self.__draw_absorber()
        self.__connect_components()
        # merge all the polygons of the pixel layer and draw a single polyline
        pixel_pl = unary_union(self.__pixel_polygons__)
        self.__draw_polyline(pixel_pl.exterior.coords, self.pixel_layer_name)
        # draw other layers above the pixel
        self.__draw_center()
        self.__draw_pixel_area()
        self.__draw_absorber_area()
        self.__draw_index()

        # center position of the absorber
        center=(-0.5*self.vertical_size-
                self.absorber_separation-
                int(self.capacitor_finger_number)*self.capacitor_finger_width-
                int(self.capacitor_finger_number-1)*self.capacitor_finger_gap,
                -0.5*self.vertical_size)

        # origin on the absorber center
        for entity in self.msp:
            entity.transform(ezdxf.math.Matrix44.translate(center[0], center[1], 0.0))

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
