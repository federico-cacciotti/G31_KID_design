from G31_KID_design import HilbertLShape
import numpy as np

N_PIXEL = 415

# pixel parameters
data = np.load('./data_v3.npy')
COUPLING_LENGTH = [data[l][3] for l in range(N_PIXEL)]
FINGER_NUMBER = [data[n][2] for n in range(N_PIXEL)]

for i in range(N_PIXEL):
    pixel = HilbertLShape(index = i+1,
                        vertical_size = 2971.3128,  # -0.6533 micron from feedline
                        line_width = 4.0,
                        coupling_capacitor_length = COUPLING_LENGTH[i],
                        coupling_capacitor_width = 100.0,
                        coupling_connector_width = 8.0,
                        coupling_capacitor_y_offset = 116.0,
                        capacitor_finger_number = FINGER_NUMBER[i],
                        capacitor_finger_gap = 4.0,
                        capacitor_finger_width = 4.0,
                        hilbert_order = 3,
                        absorber_separation = 100.0)

    pixel.save_dxf('./pixels/pixel_{:d}.dxf'.format(pixel.index))