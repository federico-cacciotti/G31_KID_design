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
    def __init__(self, index, h, l, d, w, capacitor_connector_w, capacitor_connector_h, capacitor_finger_number_v, capacitor_finger_number_h, 
                 capacitor_finger_width, capacitor_finger_gap, coupling_capacitor_v_length, coupling_capacitor_h_length, coupling_capacitor_w, 
                 coupling_capacitor_connector_h, absorber_choke_d, absorber_choke_h, absorber_choke_s, absorber_choke_w, capacitor_offset,
                 capacitor_finger_extra_end_gap=0.0, capacitor_size=0.0):

        self.index = index
        self.h = h
        self.l = l
        self.d = d
        self.w = w
        self.capacitor_connector_w = capacitor_connector_w
        self.capacitor_connector_h = capacitor_connector_h
        self.capacitor_finger_number_v = capacitor_finger_number_v
        self.capacitor_finger_number_h = capacitor_finger_number_h
        self.capacitor_finger_width = capacitor_finger_width
        self.capacitor_finger_gap = capacitor_finger_gap
        self.coupling_capacitor_v_length = coupling_capacitor_v_length
        self.coupling_capacitor_h_length = coupling_capacitor_h_length
        self.coupling_capacitor_w = coupling_capacitor_w
        self.coupling_capacitor_connector_h = coupling_capacitor_connector_h
        self.absorber_choke_d = absorber_choke_d
        self.absorber_choke_h = absorber_choke_h
        self.absorber_choke_s = absorber_choke_s
        self.absorber_choke_w = absorber_choke_w
        self.capacitor_finger_extra_end_gap = capacitor_finger_extra_end_gap
        self.capacitor_offset = capacitor_offset
        # hidden parameters
        if capacitor_size == 0.0:
            self.capacitor_size = (self.l*0.5+self.absorber_choke_d+2.0*self.absorber_choke_w+self.absorber_choke_s)*2.0
        else:
            self.capacitor_size = capacitor_size
        self.capacitor_s = 10.0
        self.capacitor_finger_length = self.capacitor_size - self.capacitor_finger_gap - 2.0*self.capacitor_connector_w - self.capacitor_finger_extra_end_gap
        self.coupling_capacitor_connector_w = 20.0

        # the four radii r1 > r2 > r3 > r4 for trigonometric corrections
        self.r1 = self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+2.0*self.absorber_choke_w
        self.r2 = self.r1 - self.absorber_choke_w
        self.r3 = self.r2 - self.absorber_choke_s
        self.r4 = self.r3 - self.absorber_choke_w

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
        self.choke_layer_name = "CHOKE"
        self.center_layer_name = "CENTER"
        self.pixel_area_layer_name = "PIXEL_AREA"
        self.absorber_area_layer_name = "ABSORBER_AREA"
        self.index_layer_name = "INDEX"
        # layer colors - AutoCAD Color Index - table on http://gohtx.com/acadcolors.php
        self.pixel_layer_color = 255
        self.choke_layer_color = 3
        self.pixel_area_layer_color = 140
        self.absorber_area_layer_color = 150
        self.center_layer_color = 120
        self.index_layer_color = 254

        # adds layers
        self.dxf.layers.add(name=self.pixel_layer_name, color=self.pixel_layer_color)
        self.dxf.layers.add(name=self.choke_layer_name, color=self.choke_layer_color)
        self.dxf.layers.add(name=self.center_layer_name, color=self.center_layer_color)
        self.dxf.layers.add(name=self.pixel_area_layer_name, color=self.pixel_area_layer_color)
        self.dxf.layers.add(name=self.absorber_area_layer_name, color=self.absorber_area_layer_color)
        self.dxf.layers.add(name=self.index_layer_name, color=self.index_layer_color)

        # adds a modelspace
        self.msp = self.dxf.modelspace()

        # list of all the polygons that draw the whole pixel
        self.__pixel_polygons__ = []

        # draw the pixel
        self.__draw_absorber_v()
        self.__draw_absorber_h()
        self.__draw_capacitor_connetor()
        self.__draw_capacitor_v()
        self.__draw_capacitor_h()
        self.__draw_coupling_capacitor_v()
        self.__draw_coupling_capacitor_h()
        self.__draw_center()
        self.__draw_index()
        self.__draw_absorber_area()

        '''
        # merge all the polygons of the pixel layer and draw a single polyline
        pixel_pl = unary_union(self.__pixel_polygons__)
        points = pixel_pl.exterior.coords
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})
        '''



    def __draw_absorber_v(self):
        # vertical polarization absorber
        points = ((-self.h*0.5-self.w, -np.sqrt(self.r4**2.0-(self.h*0.5+self.w)**2.0)),
                    (-self.h*0.5-self.w, self.l*0.5),
                    (self.h*0.5+self.w, self.l*0.5),
                    (self.h*0.5+self.w, -np.sqrt(self.r4**2.0-(self.h*0.5+self.w)**2.0)),
                    (self.h*0.5, -np.sqrt(self.r4**2.0-(self.h*0.5+self.w)**2.0)),
                    (self.h*0.5, self.l*0.5-self.w),
                    (-self.h*0.5, self.l*0.5-self.w),
                    (-self.h*0.5, -np.sqrt(self.r4**2.0-(self.h*0.5+self.w)**2.0)))
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})

    def __draw_absorber_h(self):
        # left horizontal polarization absorber
        points = ((-np.sqrt(self.r2**2.0-(self.h*0.5)**2.0), -self.h*0.5-self.w),
                  (-self.d-self.h*0.5-self.w, -self.h*0.5-self.w),
                  (-self.d-self.h*0.5-self.w, self.h*0.5+self.w),
                  (-np.sqrt(self.r4**2.0-(self.h*0.5+self.w)**2.0), self.h*0.5+self.w),
                  (-np.sqrt(self.r4**2.0-(self.h*0.5+self.w)**2.0), self.h*0.5),
                  (-self.d-self.h*0.5-2.0*self.w, self.h*0.5),
                  (-self.d-self.h*0.5-2.0*self.w, -self.h*0.5),
                  (-np.sqrt(self.r2**2.0-(self.h*0.5)**2.0), -self.h*0.5))
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})

        # right horizontal polarization absorber
        points = ((np.sqrt(self.r2**2.0-(self.h*0.5)**2.0), -self.h*0.5-self.w),
                  (self.d+self.h*0.5+self.w, -self.h*0.5-self.w),
                  (self.d+self.h*0.5+self.w, self.h*0.5+self.w),
                  (np.sqrt(self.r4**2.0-(self.h*0.5+self.w)**2.0), self.h*0.5+self.w),
                  (np.sqrt(self.r4**2.0-(self.h*0.5+self.w)**2.0), self.h*0.5),
                  (self.d+self.h*0.5+2.0*self.w, self.h*0.5),
                  (self.d+self.h*0.5+2.0*self.w, -self.h*0.5),
                  (np.sqrt(self.r2**2.0-(self.h*0.5)**2.0), -self.h*0.5))
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})


    # draws the capacitor connectors
    def __draw_capacitor_connetor(self):
        # this function computes the bulge parameter for circular section polylines
        def bulge(A, B):
            return 2.0/np.linalg.norm(A-B) * (np.linalg.norm(A) - np.sqrt(np.linalg.norm(A)**2.0-0.25*np.linalg.norm(A-B)**2.0))
        
        # quarter choke (bottom left) # OK
        '''
        A = np.array([-self.absorber_choke_h*0.5, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h])
        B = np.array([-self.absorber_choke_h*0.5, -np.sqrt(r2**2.0-(self.absorber_choke_h*0.5)**2.0)])
        C = np.array([-np.sqrt(r2**2.0-(self.h*0.5+self.w+self.absorber_choke_h+self.absorber_choke_w)**2.0), -self.h*0.5-self.w-self.absorber_choke_h-self.absorber_choke_w])
        D = np.array([-np.sqrt(r3**2.0-(self.h*0.5+self.w+self.absorber_choke_h+self.absorber_choke_w)**2.0), -self.h*0.5-self.w-self.absorber_choke_h-self.absorber_choke_w])
        E = np.array([-self.h*0.5, -np.sqrt(r3**2.0-(self.h*0.5)**2.0)])
        F = np.array([-self.h*0.5, -self.l*0.5])
        G = np.array([-self.h*0.5-self.w, -self.l*0.5])
        H = np.array([-self.h*0.5-self.w, -np.sqrt(r4**2.0-(self.h*0.5+self.w)**2.0)])
        I = np.array([-np.sqrt(r4**2.0-(self.h*0.5+self.w+self.absorber_choke_h)**2.0), -self.h*0.5-self.w-self.absorber_choke_h])
        J = np.array([-np.sqrt(r1**2.0-(self.h*0.5+self.w+self.absorber_choke_h)**2.0), -self.h*0.5-self.w-self.absorber_choke_h])
        K = np.array([-self.absorber_choke_h*0.5-self.capacitor_connector_w, -np.sqrt(r1**2.0-(self.absorber_choke_h*0.5+self.capacitor_connector_w)**2.0)])
        L = np.array([-self.absorber_choke_h*0.5-self.capacitor_connector_w, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h])

        points = (A, (B[0], B[1], 0.0, 0.0, -bulge(B, C)), C, (D[0], D[1], 0.0, 0.0, bulge(D, E)), E, F, G , 
                  (H[0], H[1], 0.0, 0.0, -bulge(H, I)), I, (J[0], J[1], 0.0, 0.0, bulge(J, K)), K, L)
        '''
        A = np.array([-self.absorber_choke_h*0.5, -np.sqrt(self.r2**2.0-(self.absorber_choke_h*0.5)**2.0)])
        B = np.array([-np.sqrt(self.r2**2.0-(self.h*0.5+self.w+self.absorber_choke_h+self.absorber_choke_w)**2.0), -self.h*0.5-self.w-self.absorber_choke_h-self.absorber_choke_w])
        C = np.array([-np.sqrt(self.r3**2.0-(self.h*0.5+self.w+self.absorber_choke_h+self.absorber_choke_w)**2.0), -self.h*0.5-self.w-self.absorber_choke_h-self.absorber_choke_w])
        D = np.array([-self.h*0.5, -np.sqrt(self.r3**2.0-(self.h*0.5)**2.0)])
        #E = np.array([D[0], D[1]+self.absorber_choke_w])
        F = np.array([-self.h*0.5-self.w, -np.sqrt(self.r4**2.0-(self.h*0.5+self.w)**2.0)])
        E = np.array([F[0]+self.w, F[1]])
        G = np.array([-np.sqrt(self.r4**2.0-(self.h*0.5+self.w+self.absorber_choke_h)**2.0), -self.h*0.5-self.w-self.absorber_choke_h])
        H = np.array([-np.sqrt(self.r1**2.0-(self.h*0.5+self.w+self.absorber_choke_h)**2.0), -self.h*0.5-self.w-self.absorber_choke_h])
        I = np.array([-self.absorber_choke_h*0.5-self.capacitor_connector_w, -np.sqrt(self.r1**2.0-(self.absorber_choke_h*0.5+self.capacitor_connector_w)**2.0)])
        J = np.array([I[0]+self.capacitor_connector_w, I[1]])
        points = ((A[0], A[1], 0.0, 0.0, -bulge(A, B)), B, (C[0], C[1], 0.0, 0.0, bulge(C, D)), D, E, (F[0], F[1], 0.0, 0.0, -bulge(F, G)), G, (H[0], H[1], 0.0, 0.0, bulge(H, I)), I, J)
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.choke_layer_name})

        # quarter choke (bottom right) # OK
        '''
        A = np.array([self.absorber_choke_h*0.5, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h])
        B = np.array([self.absorber_choke_h*0.5, -np.sqrt(r2**2.0-(self.absorber_choke_h*0.5)**2.0)])
        C = np.array([np.sqrt(r2**2.0-(self.h*0.5+self.w+self.absorber_choke_h+self.absorber_choke_w)**2.0), -self.h*0.5-self.w-self.absorber_choke_h-self.absorber_choke_w])
        D = np.array([np.sqrt(r3**2.0-(self.h*0.5+self.w+self.absorber_choke_h+self.absorber_choke_w)**2.0), -self.h*0.5-self.w-self.absorber_choke_h-self.absorber_choke_w])
        E = np.array([self.h*0.5, -np.sqrt(r3**2.0-(self.h*0.5)**2.0)])
        F = np.array([self.h*0.5, -self.l*0.5])
        G = np.array([self.h*0.5+self.w, -self.l*0.5])
        H = np.array([self.h*0.5+self.w, -np.sqrt(r4**2.0-(self.h*0.5+self.w)**2.0)])
        I = np.array([np.sqrt(r4**2.0-(self.h*0.5+self.w+self.absorber_choke_h)**2.0), -self.h*0.5-self.w-self.absorber_choke_h])
        J = np.array([np.sqrt(r1**2.0-(self.h*0.5+self.w+self.absorber_choke_h)**2.0), -self.h*0.5-self.w-self.absorber_choke_h])
        K = np.array([self.absorber_choke_h*0.5+self.capacitor_connector_w, -np.sqrt(r1**2.0-(self.absorber_choke_h*0.5+self.capacitor_connector_w)**2.0)])
        L = np.array([self.absorber_choke_h*0.5+self.capacitor_connector_w, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h])

        points = (A, (B[0], B[1], 0.0, 0.0, bulge(B, C)), C, (D[0], D[1], 0.0, 0.0, -bulge(D, E)), E, F, G , 
                  (H[0], H[1], 0.0, 0.0, bulge(H, I)), I, (J[0], J[1], 0.0, 0.0, -bulge(J, K)), K, L)
        '''
        A = np.array([self.absorber_choke_h*0.5, -np.sqrt(self.r2**2.0-(self.absorber_choke_h*0.5)**2.0)])
        B = np.array([np.sqrt(self.r2**2.0-(self.h*0.5+self.w+self.absorber_choke_h+self.absorber_choke_w)**2.0), -self.h*0.5-self.w-self.absorber_choke_h-self.absorber_choke_w])
        C = np.array([np.sqrt(self.r3**2.0-(self.h*0.5+self.w+self.absorber_choke_h+self.absorber_choke_w)**2.0), -self.h*0.5-self.w-self.absorber_choke_h-self.absorber_choke_w])
        D = np.array([self.h*0.5, -np.sqrt(self.r3**2.0-(self.h*0.5)**2.0)])
        #E = np.array([D[0], D[1]+self.absorber_choke_w])
        F = np.array([self.h*0.5+self.w, -np.sqrt(self.r4**2.0-(self.h*0.5+self.w)**2.0)])
        E = np.array([F[0]-self.w, F[1]])
        G = np.array([np.sqrt(self.r4**2.0-(self.h*0.5+self.w+self.absorber_choke_h)**2.0), -self.h*0.5-self.w-self.absorber_choke_h])
        H = np.array([np.sqrt(self.r1**2.0-(self.h*0.5+self.w+self.absorber_choke_h)**2.0), -self.h*0.5-self.w-self.absorber_choke_h])
        I = np.array([self.absorber_choke_h*0.5+self.capacitor_connector_w, -np.sqrt(self.r1**2.0-(self.absorber_choke_h*0.5+self.capacitor_connector_w)**2.0)])
        J = np.array([I[0]-self.capacitor_connector_w, I[1]])
        points = ((A[0], A[1], 0.0, 0.0, bulge(A, B)), B, (C[0], C[1], 0.0, 0.0, -bulge(C, D)), D, E, (F[0], F[1], 0.0, 0.0, bulge(F, G)), G, (H[0], H[1], 0.0, 0.0, -bulge(H, I)), I, J)
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.choke_layer_name})

        # half choke (top) # OK
        '''
        A = np.array([-self.l*0.5, self.h*0.5])
        B = np.array([-np.sqrt(r3**2.0-(self.h*0.5)**2.0), self.h*0.5])
        C = np.array([np.sqrt(r3**2.0-(self.h*0.5)**2.0), self.h*0.5])
        D = np.array([self.l*0.5, self.h*0.5])
        E = np.array([self.l*0.5, self.h*0.5+self.w])
        F = np.array([np.sqrt(r4**2.0-(self.h*0.5+self.w)**2.0), self.h*0.5+self.w])
        G = np.array([-np.sqrt(r4**2.0-(self.h*0.5+self.w)**2.0), self.h*0.5+self.w])
        H = np.array([-self.l*0.5, self.h*0.5+self.w])
        points = (A, (B[0], B[1], 0.0, 0.0, -bulge(B, C)), C, D, E, (F[0], F[1], 0.0, 0.0, bulge(F, G)), G, H)
        '''
        A = np.array([-np.sqrt(self.r3**2.0-(self.h*0.5)**2.0), self.h*0.5])
        B = np.array([-A[0], A[1]])
        D = np.array([np.sqrt(self.r4**2.0-(self.h*0.5+self.w)**2.0), self.h*0.5+self.w])
        C = np.array([D[0], D[1]-self.w])
        #D = np.array([C[0], C[1]+self.w])
        E = np.array([-D[0], D[1]])
        F = np.array([-C[0], C[1]])
        points = ((A[0], A[1], 0.0, 0.0, -bulge(A, B)), B, C, (D[0], D[1], 0.0, 0.0, bulge(D, E)), E, F)
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.choke_layer_name})

        # quarter choke (top left) # OK
        '''
        A = np.array([-self.l*0.5, -self.h*0.5])
        B = np.array([-np.sqrt(r2**2.0-(self.h*0.5)**2.0), -self.h*0.5])
        C = np.array([-self.absorber_choke_h*0.5, np.sqrt(r2**2.0-(self.absorber_choke_h*0.5)**2.0)])
        D = np.array([-self.absorber_choke_h*0.5, self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+2.0*self.absorber_choke_w+self.capacitor_connector_h])
        E = np.array([-self.absorber_choke_h*0.5-self.capacitor_connector_w, self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+2.0*self.absorber_choke_w+self.capacitor_connector_h])
        F = np.array([-self.absorber_choke_h*0.5-self.capacitor_connector_w, np.sqrt(r1**2.0-(self.absorber_choke_h*0.5+self.capacitor_connector_w)**2.0)])
        G = np.array([-np.sqrt(r1**2.0-(self.h*0.5+self.w)**2.0), -self.h*0.5-self.w])
        H = np.array([-self.l*0.5, -self.h*0.5-self.w])
        points = (A, (B[0], B[1], 0.0, 0.0, -bulge(B, C)), C, D, E, (F[0], F[1], 0.0, 0.0, bulge(F, G)), G, H)
        '''
        A = np.array([-np.sqrt(self.r2**2.0-(self.h*0.5)**2.0), -self.h*0.5])
        B = np.array([-self.absorber_choke_h*0.5, np.sqrt(self.r2**2.0-(self.absorber_choke_h*0.5)**2.0)])
        #C = np.array([B[0], B[1]+self.absorber_choke_w])
        D = np.array([-self.absorber_choke_h*0.5-self.capacitor_connector_w, np.sqrt(self.r1**2.0-(self.absorber_choke_h*0.5+self.capacitor_connector_w)**2.0)])
        C = np.array([D[0]+self.capacitor_connector_w, D[1]])
        E = np.array([-np.sqrt(self.r1**2.0-(self.h*0.5+self.w)**2.0), -self.h*0.5-self.w])
        F = np.array([A[0], A[1]-self.w])
        points = ((A[0], A[1], 0.0, 0.0, -bulge(A, B)), B, C, (D[0], D[1], 0.0, 0.0, bulge(D, E)), E, F)
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.choke_layer_name})

        # quarter choke (top right)
        '''
        A = np.array([self.l*0.5, -self.h*0.5])
        B = np.array([np.sqrt(r2**2.0-(self.h*0.5)**2.0), -self.h*0.5])
        C = np.array([self.absorber_choke_h*0.5, np.sqrt(r2**2.0-(self.absorber_choke_h*0.5)**2.0)])
        D = np.array([self.absorber_choke_h*0.5, self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+2.0*self.absorber_choke_w+self.capacitor_connector_h])
        E = np.array([self.absorber_choke_h*0.5+self.capacitor_connector_w, self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+2.0*self.absorber_choke_w+self.capacitor_connector_h])
        F = np.array([self.absorber_choke_h*0.5+self.capacitor_connector_w, np.sqrt(r1**2.0-(self.absorber_choke_h*0.5+self.capacitor_connector_w)**2.0)])
        G = np.array([np.sqrt(r1**2.0-(self.h*0.5+self.w)**2.0), -self.h*0.5-self.w])
        H = np.array([self.l*0.5, -self.h*0.5-self.w])
        points = (A, (B[0], B[1], 0.0, 0.0, bulge(B, C)), C, D, E, (F[0], F[1], 0.0, 0.0, -bulge(F, G)), G, H)
        '''
        A = np.array([np.sqrt(self.r2**2.0-(self.h*0.5)**2.0), -self.h*0.5])
        B = np.array([self.absorber_choke_h*0.5, np.sqrt(self.r2**2.0-(self.absorber_choke_h*0.5)**2.0)])
        #C = np.array([B[0], B[1]+self.absorber_choke_w])
        D = np.array([self.absorber_choke_h*0.5+self.capacitor_connector_w, np.sqrt(self.r1**2.0-(self.absorber_choke_h*0.5+self.capacitor_connector_w)**2.0)])
        C = np.array([D[0]-self.capacitor_connector_w, D[1]])
        E = np.array([np.sqrt(self.r1**2.0-(self.h*0.5+self.w)**2.0), -self.h*0.5-self.w])
        F = np.array([A[0], A[1]-self.w])
        points = ((A[0], A[1], 0.0, 0.0, bulge(A, B)), B, C, (D[0], D[1], 0.0, 0.0, -bulge(D, E)), E, F)
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.choke_layer_name})
    
    
    # draws the interdigital capacitor
    def __draw_capacitor_v(self):
        finger_number_int = int(self.capacitor_finger_number_v)
        capacitor_vertical_width = finger_number_int*self.capacitor_finger_width+(finger_number_int-1)*self.capacitor_finger_gap
        # draw fingers
        y_shift = -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_s-self.capacitor_finger_width
        x_shift = -self.capacitor_size*0.5+self.capacitor_connector_w
        for i in range(finger_number_int):
            corner0 = (((i+1)%2)*(self.capacitor_finger_gap+self.capacitor_finger_extra_end_gap) + x_shift-self.capacitor_offset, -i*(self.capacitor_finger_width+self.capacitor_finger_gap) + y_shift)
            y_size = self.capacitor_finger_width
            x_size = self.capacitor_finger_length
            self.msp.add_lwpolyline(fc.draw_rectangle_corner_dimensions_points(corner0, x_size, y_size), close=True, dxfattribs={"layer": self.pixel_layer_name})

        # connectors
        A = np.array([-self.absorber_choke_h*0.5, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h])
        B = np.array([-self.capacitor_size*0.5-self.capacitor_offset, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h])
        C = np.array([-self.capacitor_size*0.5-self.capacitor_offset, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_s-capacitor_vertical_width])
        D = np.array([-self.capacitor_size*0.5+self.capacitor_connector_w-self.capacitor_offset, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_s-capacitor_vertical_width])
        E = np.array([-self.capacitor_size*0.5+self.capacitor_connector_w-self.capacitor_offset, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_connector_w])
        F = np.array([-self.absorber_choke_h*0.5, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_connector_w])
        points = (A, B, C, D, E, F)
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})

        # connectors
        A = np.array([self.absorber_choke_h*0.5, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h])
        B = np.array([self.capacitor_size*0.5-self.capacitor_offset, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h])
        C = np.array([self.capacitor_size*0.5-self.capacitor_offset, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_s-capacitor_vertical_width])
        D = np.array([self.capacitor_size*0.5-self.capacitor_offset-self.capacitor_connector_w, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_s-capacitor_vertical_width])
        E = np.array([self.capacitor_size*0.5-self.capacitor_connector_w-self.capacitor_offset, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_connector_w])
        F = np.array([self.absorber_choke_h*0.5, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_connector_w])
        points = (A, B, C, D, E, F)
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})

        # pinky finger
        if self.capacitor_finger_number_v-finger_number_int != 0.0:
            pinky_length = self.capacitor_finger_length*(self.capacitor_finger_number_v-finger_number_int)
            corner0 = (x_shift-self.capacitor_offset, y_shift+self.capacitor_finger_width+self.capacitor_finger_gap)
            y_size = self.capacitor_finger_width
            x_size = pinky_length
            self.msp.add_lwpolyline(fc.draw_rectangle_corner_dimensions_points(corner0, x_size, y_size), close=True, dxfattribs={"layer": self.pixel_layer_name})

    # draws the interdigital capacitor
    def __draw_capacitor_h(self):
        finger_number_int = int(self.capacitor_finger_number_h)
        capacitor_vertical_width = finger_number_int*self.capacitor_finger_width+(finger_number_int-1)*self.capacitor_finger_gap
        # draw fingers
        y_shift = self.l*0.5+self.absorber_choke_d+self.absorber_choke_s+2.0*self.absorber_choke_w+self.capacitor_connector_h+self.capacitor_s
        x_shift = -self.capacitor_size*0.5+self.capacitor_connector_w
        for i in range(finger_number_int):
            corner0 = (((i)%2)*(self.capacitor_finger_gap+self.capacitor_finger_extra_end_gap) + x_shift-self.capacitor_offset, i*(self.capacitor_finger_width+self.capacitor_finger_gap) + y_shift)
            y_size = self.capacitor_finger_width
            x_size = self.capacitor_finger_length
            self.msp.add_lwpolyline(fc.draw_rectangle_corner_dimensions_points(corner0, x_size, y_size), close=True, dxfattribs={"layer": self.pixel_layer_name})

        # connectors
        A = np.array([-self.absorber_choke_h*0.5, -(-self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h)])
        B = np.array([-self.capacitor_size*0.5-self.capacitor_offset, -(-self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h)])
        C = np.array([-self.capacitor_size*0.5-self.capacitor_offset, -(-self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_s-capacitor_vertical_width)])
        D = np.array([-self.capacitor_size*0.5+self.capacitor_connector_w-self.capacitor_offset, -(-self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_s-capacitor_vertical_width)])
        E = np.array([-self.capacitor_size*0.5+self.capacitor_connector_w-self.capacitor_offset, -(-self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_connector_w)])
        F = np.array([-self.absorber_choke_h*0.5, -(-self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_connector_w)])
        points = (A, B, C, D, E, F)
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})

        # connectors
        A = np.array([self.absorber_choke_h*0.5, -(-self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h)])
        B = np.array([self.capacitor_size*0.5-self.capacitor_offset, -(-self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h)])
        C = np.array([self.capacitor_size*0.5-self.capacitor_offset, -(-self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_s-capacitor_vertical_width)])
        D = np.array([self.capacitor_size*0.5-self.capacitor_connector_w-self.capacitor_offset, -(-self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_s-capacitor_vertical_width)])
        E = np.array([self.capacitor_size*0.5-self.capacitor_connector_w-self.capacitor_offset, -(-self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_connector_w)])
        F = np.array([self.absorber_choke_h*0.5, -(-self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_connector_w)])
        points = (A, B, C, D, E, F)
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})

        # pinky finger
        if self.capacitor_finger_number_h-finger_number_int != 0.0:
            pinky_length = self.capacitor_finger_length*(self.capacitor_finger_number_h-finger_number_int)
            corner0 = (x_shift+self.capacitor_finger_length+self.capacitor_finger_gap+self.capacitor_finger_extra_end_gap-self.capacitor_offset, y_shift-self.capacitor_finger_width-self.capacitor_finger_gap)
            y_size = self.capacitor_finger_width
            x_size = -pinky_length
            self.msp.add_lwpolyline(fc.draw_rectangle_corner_dimensions_points(corner0, x_size, y_size), close=True, dxfattribs={"layer": self.pixel_layer_name})

    def __draw_coupling_capacitor_v(self):
        finger_number_int = int(self.capacitor_finger_number_v)
        capacitor_vertical_width = finger_number_int*self.capacitor_finger_width+(finger_number_int-1)*self.capacitor_finger_gap
        A = np.array([self.capacitor_size*0.5-self.capacitor_offset, -self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_s-capacitor_vertical_width])
        B = np.array([A[0]+self.coupling_capacitor_connector_h+self.coupling_capacitor_w+self.capacitor_offset, A[1]])
        C = np.array([B[0], B[1]+self.coupling_capacitor_v_length])
        D = np.array([C[0]-self.coupling_capacitor_w, C[1]])
        E = np.array([D[0], D[1]-self.coupling_capacitor_v_length+self.coupling_capacitor_connector_w])
        F = np.array([A[0], E[1]])
        points = (A, B, C, D, E, F)
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})
    
    def __draw_coupling_capacitor_h(self):
        finger_number_int = int(self.capacitor_finger_number_h)
        capacitor_vertical_width = finger_number_int*self.capacitor_finger_width+(finger_number_int-1)*self.capacitor_finger_gap
        A = np.array([self.capacitor_size*0.5-self.capacitor_offset, -(-self.l*0.5-self.absorber_choke_d-self.absorber_choke_s-2.0*self.absorber_choke_w-self.capacitor_connector_h-self.capacitor_s-capacitor_vertical_width)])
        B = np.array([A[0]+self.coupling_capacitor_connector_h+self.coupling_capacitor_w+self.capacitor_offset, A[1]])
        C = np.array([B[0], B[1]-self.coupling_capacitor_h_length])
        D = np.array([C[0]-self.coupling_capacitor_w, C[1]])
        E = np.array([D[0], D[1]+self.coupling_capacitor_h_length-self.coupling_capacitor_connector_w])
        F = np.array([A[0], E[1]])
        points = (A, B, C, D, E, F)
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.pixel_layer_name})

    # draws a cross over the absorber to find its center
    def __draw_center(self):
        # draw the diagonals to find the center
        points = ((-self.l*0.5, -self.l*0.5), (self.l*0.5, self.l*0.5))
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.center_layer_name})
        points = ((-self.l*0.5, self.l*0.5), (self.l*0.5, -self.l*0.5))
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.center_layer_name})

    # draws a box over the absorber
    def __draw_absorber_area(self):
        points = ((-self.l*0.5, -self.l*0.5), (-self.l*0.5, self.l*0.5),
                  (self.l*0.5, self.l*0.5), (self.l*0.5, -self.l*0.5))
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": self.absorber_area_layer_name})


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
