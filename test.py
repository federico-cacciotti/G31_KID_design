# test script

# import the package
import KID_drawer as KID

# define a Pixel object
pixel = KID.Pixel(index = 1,
				  vertical_size = 3000.0,
				  line_width = 4.0,
				  coupling_capacitor_length = 2500.0,
				  coupling_capacitor_width = 80.0,
				  coupling_connector_width = 20.0,
				  coupling_capacitor_y_offset = 120.0,
				  capacitor_finger_number = 50.65,
				  capacitor_finger_gap = 4.0,
				  capacitor_finger_width = 4.0,
				  hilbert_order = 4,
				  absorber_separation = 200.0)

# print the pixel parameters
pixel.print_info()

# save the .dxf file
pixel.save_dxf(filename = 'examples/test/pixel.dxf')
