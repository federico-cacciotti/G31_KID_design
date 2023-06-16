# G31_KID_design package
This Python package allows one to quickly generate an array of Kinetic Inductance Detectors as well as single pixels. I developed this package during my master thesis period and it is still an ongoing project for my PhD.

The use of this package is recommended under Linux or Mac OS. This software is developed under Mac OS.

# Required third-party packages
In order to make things working the following packages are mandatory.
- `ezdxf`: version >=0.17.2 (thank you `mozman` for allowing me to ease my back and save time) [here](https://github.com/mozman/ezdxf) you can find the repo to this package;
- `shapely`: version >=1.8.0. [Here](https://github.com/shapely) the link to the repo!

# Overview
With this package it is possible to generate .dxf design files of Kinetic Inductance Detectors (KIDs) starting from geometrical parameters defined below:

- `index`: int, the id of the pixel
- `vertical_size`: float, edge size of the absorber
- `line_width`: float, width of the conductive path
- `coupling_capacitor_length`: float, length of the coupling capacitor
- `coupling_capacitor_width`: float, width of the coupling capacitor
- `coupling_connector_width`: float, width of the conductive segment that goes
	from the pixel to the coupling capacitor
- `coupling_capacitor_y_offset`: float, vertical separation between the pixel
	and the coupling capacitor
- `capacitor_finger_number`: float, number of fingers of the interdigital capacitor
	with decimal digits meaning an extra finger of variable length
- `capacitor_finger_gap`: float, gap between interdigitated fingers
- `capacitor_finger_width`: float, width of the interdigitated fingers
- `hilbert_order`: int, hilbert order of the absorber (it is reccommended to not
	exceed the 7th order for computational reasons)
- `absorber_separation`: float, horizontal separation of the absorber from the
	capacitor

These parameters are shown in the following image (with `capacitor_finger_number = 3.6` and `hilbert_order = 3`).

![schematic](/images/schematic.png)

The final dxf drawing has many layers:

- PIXEL: the actual layer where the KID is shown
- PIXEL_AREA: a layer where a rectangle encloses the whole pixel
- ABSORBER_AREA: a layer where a square encloses the absorber section of the KID
- CENTER: a layer where the two diagonals of the ABSORBER_AREA square are shown
- INDEX: a layer where the `index` value of the pixel is shown

The output drawing has the absorber centered to the origin

All the distances are expressed in units of microns.
The following image shows an example of a real KID generated with this package.

![example](/images/example.png)

# Examples
In the `examples` directory you can find many examples showing how to use this package.
