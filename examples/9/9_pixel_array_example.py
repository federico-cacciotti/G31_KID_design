from KID_drawer import Pixel, Array
import csv

# function that return a float, int or string from a string
def str_to_type(strg):
    try:
        val = float(strg)
        if val.is_integer():
            return int(val) # int type
        else:
            return val # float type
    except:
        return strg # string type

# read data from .csv file
with open('examples/9/pixel_parameters.csv', mode = 'r') as file:
    data = {el[0]: [str_to_type(val) for val in el[1:]] for el in zip(*csv.reader(file))}

# draw pixels
for (i,idx) in enumerate(data['index']):
    pixel = Pixel(index = idx,
                  vertical_size = 16000,
                  line_width = 4.0,
                  coupling_capacitor_length = data['cc_length'][i],
                  coupling_capacitor_width = 100.0,
                  coupling_connector_width = 8.0,
                  coupling_capacitor_y_offset = 116.0,
                  capacitor_finger_number = data['n_fingers'][i],
                  capacitor_finger_gap = 4.0,
                  capacitor_finger_width = 4.0,
                  hilbert_order = 5,
                  absorber_separation = 100.0)
    pixel.save_dxf('examples/9/pixels/pixel_{:d}.dxf'.format(idx))

# draw array and save figure
array = Array("examples/9/pixels", 9, data['x'], data['y'], data['rot'], data['mir'])
array.saveFig("examples/9/array.png", dpi=350)
