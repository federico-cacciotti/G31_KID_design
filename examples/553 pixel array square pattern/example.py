from G31_KID_design import HilbertLShape, Array
from G31_KID_design.Patterns import circularSquareLattice as csl
import numpy as np

WAFER_DIAMETER = 50000.0 # microns
n, x, y, r = csl(radius=0.5*WAFER_DIAMETER, pitch=1830.0, element_dimension=1000.0, rotation=-1)

for i,(x_i,y_i) in enumerate(zip(x,y)):
    
    R = np.sqrt(x_i**2.0 + y_i**2.0)/(0.5*WAFER_DIAMETER)
    
    pixel = HilbertLShape(index = i,
                  vertical_size = 1000,
                  line_width = 2.0,
                  coupling_capacitor_length = 800,
                  coupling_capacitor_width = 50.0,
                  coupling_connector_width = 15.0,
                  coupling_capacitor_y_offset = 55.0,
                  capacitor_finger_number = 150*(1-R),
                  capacitor_finger_gap = 2.0,
                  capacitor_finger_width = 2.0,
                  hilbert_order = 3,
                  absorber_separation = 10.0)

    pixel.save_dxf('./pixels/pixel_{:d}.dxf'.format(i+1))

array = Array('./pixels', n, x, y, r, output_dxf='array.dxf', 
                                      feedline_dxf='feedline.dxf',
                                      focal_plane_dxf='focal_plane_limit.dxf',
                                      wafer_limits='wafer_limits.dxf')
array.saveFig("array.png", dpi=600)