from G31_KID_design import HilbertLShape

pixel = HilbertLShape(index = 1,
              vertical_size = 1500.0,
              line_width = 4.0,
              coupling_capacitor_length = 1850.0,
              coupling_capacitor_width = 100.0,
              coupling_connector_width = 20.0,
              coupling_capacitor_y_offset = 130.0,
              capacitor_finger_number = 5.50,
              capacitor_finger_gap = 15.0,
              capacitor_finger_width = 7.0,
              hilbert_order = 4,
              absorber_separation = 130.0)
# draw pixel and save figure
pixel.save_dxf('./pixels/pixel_1.dxf')
pixel.saveFig('./pixel_1.png', dpi=350)
