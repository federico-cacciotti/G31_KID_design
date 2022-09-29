import time
import KID_drawer as KID
import numpy as np

startTime = time.time()

N_PIXEL = 415

# pixel parameters
data = np.load('data_v3.npy')
COUPLING_LENGTH = [data[l][3] for l in range(N_PIXEL)]
FINGER_NUMBER = [data[n][2] for n in range(N_PIXEL)]

for i in range(N_PIXEL):
    pixel = KID.Pixel(  index = i+1,
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

    pixel.save_dxf('examples/{:d}/pixels/pixel_{:d}.dxf'.format(N_PIXEL, pixel.index))

executionTime = (time.time() - startTime)
print('Execution time in seconds: ' + str(executionTime))
