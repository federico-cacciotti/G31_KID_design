import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch
from matplotlib.font_manager import FontProperties

def circularTriangleLattice(radius, pitch, element_dimension, rotation=0, central_pixel_magic_number=0):
    '''
    This function generates the coordinates of a triangular lattice inside a 
    circle of a given radius

    Parameters
    ----------
    radius : float
        The radius of the circle in microns.
    pitch : float
        The unit cell length of the lattice in microns.
    element_dimension : float
        The dimension of a node of the lattice, it coincides with the absorber 
        side in microns.
    rotation : int, optional
        This parameter can be 1, 0 or -1. If 1 all the even rows (starting from
        the lower one) will be rotated by 180 degrees, if -1 all the odd rows 
        will be rotated by 180 degrees, if 0 no rotation will be applied.
    central_pixel_magic_number : int, optional
        1 or 0. Default is 0.

    Returns
    -------
    n : int
        Number of nodes found.
    x : list of floats
        The x coordinates of the lattice nodes in microns.
    y : list of floats
        The y coordinates of the lattice nodes in microns.
    r : list of floats
        The rotations to be applied at each node in degrees.

    '''
    n = 0
    x = []
    y = []
    r = []
    
    x_step = pitch
    y_step = pitch * np.sqrt(3)*0.5
    
    # both the following numbers must be odd (in order to find the central pixel)
    maximum_number_diameter_x = int(radius*2.0 // x_step)
    if maximum_number_diameter_x % 2 == 0:
        maximum_number_diameter_x += 1
    
    maximum_number_diameter_y = int(radius*2.0 // y_step)
    if maximum_number_diameter_y % 2 == 0:
        maximum_number_diameter_y += 1
        
    x_min = -(maximum_number_diameter_x-1)*0.5*x_step
    y_min = -(maximum_number_diameter_y-1)*0.5*y_step

    for i,y_i in enumerate(np.linspace(y_min, -y_min, num=maximum_number_diameter_y)):
        for j,x_j in enumerate(np.linspace(x_min, -x_min, num=maximum_number_diameter_x)):
            if (y_i**2. + (x_j+((i+central_pixel_magic_number)%2)*x_step*0.5)**2.0) <= (radius-element_dimension/np.sqrt(2))**2.0:
                x.append(x_j+((i+central_pixel_magic_number)%2)*x_step*0.5)
                y.append(y_i)
                
                # check rotation parameter
                if rotation == 1:
                    r.append(180*(i%2))
                elif rotation == -1:
                    r.append(180*((i+1)%2))
                else:
                    r.append(0)
                # increase the number of nodes found
                n += 1
                
    fig = plt.figure()
    plt.xlim([-1.2*radius, 1.2*radius])
    plt.ylim([-1.2*radius, 1.2*radius])
    ax0 = plt.gca()
    ax0.set_xlabel('x position [microns]')
    ax0.set_ylabel('y position [microns]')
    ax0.set_aspect('equal')
    fp = FontProperties(family='Helvetica', style='normal', weight='light')
    # draw squares
    for i, (xi, yi, ri) in enumerate(zip(x, y, r)):
        rectangle = Rectangle((xi-element_dimension*0.5, yi-element_dimension*0.5), element_dimension, element_dimension,
                              edgecolor='black', fill=False, linewidth=0.5)
        ax0.add_patch(rectangle)
        
        tp = TextPath((xi-element_dimension*0.5, yi-element_dimension*0.25), "{:d}".format(i), size=element_dimension*0.5, prop=fp)
        ax0.add_patch(PathPatch(tp, color="black"))
    
    # draw circle of radius = radius
    circle = Circle((0.0, 0.0), radius=radius, edgecolor='red', fill=False, linewidth=0.5)
    ax0.add_patch(circle)
    plt.show()
    
    return n, x, y, r


def circularSquareLattice(radius, pitch, element_dimension, rotation=0):
    '''
    This function generates the coordinates of a square lattice inside a 
    circle of a given radius

    Parameters
    ----------
    radius : float
        The radius of the circle in microns.
    pitch : float
        The unit cell length of the lattice in microns.
    element_dimension : float
        The dimension of a node of the lattice, it coincides with the absorber 
        side in microns.
    rotation : int, optional
        This parameter can be 1, 0 or -1. If 1 all the even rows (starting from
        the lower one) will be rotated by 180 degrees, if -1 all the odd rows 
        will be rotated by 180 degrees, if 0 no rotation will be applied.

    Returns
    -------
    n : int
        Number of nodes found.
    x : list of floats
        The x coordinates of the lattice nodes in microns.
    y : list of floats
        The y coordinates of the lattice nodes in microns.
    r : list of floats
        The rotations to be applied at each node in degrees.

    '''
    n = 0
    x = []
    y = []
    r = []
    
    maximum_number = int(radius*2.0 // pitch)
    x_min = -(radius // pitch)*pitch
    y_min = -(radius // pitch)*pitch

    for i,y_i in enumerate(np.linspace(y_min, -y_min, num=maximum_number)):
        for j,x_j in enumerate(np.linspace(x_min, -x_min, num=maximum_number)):
            if (y_i**2. + (x_j)**2.) <= (radius-element_dimension/np.sqrt(2))**2.:
                x.append(x_j)
                y.append(y_i)
                
                # check rotation parameter
                if rotation == 1:
                    r.append(180*(i%2))
                elif rotation == -1:
                    r.append(180*((i+1)%2))
                else:
                    r.append(0)
                # increase the number of nodes found
                n += 1

    fig = plt.figure()
    plt.xlim([-1.2*radius, 1.2*radius])
    plt.ylim([-1.2*radius, 1.2*radius])
    ax0 = plt.gca()
    ax0.set_xlabel('x position [microns]')
    ax0.set_ylabel('y position [microns]')
    ax0.set_aspect('equal')
    fp = FontProperties(family='Helvetica', style='normal', weight='light')
    # draw squares
    for i, (xi, yi, ri) in enumerate(zip(x, y, r)):
        rectangle = Rectangle((xi-element_dimension*0.5, yi-element_dimension*0.5), element_dimension, element_dimension,
                              edgecolor='black', fill=False, linewidth=0.5)
        ax0.add_patch(rectangle)
        
        tp = TextPath((xi-element_dimension*0.5, yi-element_dimension*0.25), "{:d}".format(i), size=element_dimension*0.5, prop=fp)
        ax0.add_patch(PathPatch(tp, color="black"))
    
    # draw circle of radius = radius
    circle = Circle((0.0, 0.0), radius=radius, edgecolor='red', fill=False, linewidth=0.5)
    ax0.add_patch(circle)
    plt.show()
                
    return n, x, y, r



def squareTriangleLattice(pitch, nx_elements, ny_elements, element_dimension, rotation=0, central_pixel_magic_number=0):
    '''
    This function generates the coordinates of a triangular lattice inside a 
    square of a given side

    Parameters
    ----------
    pitch : float
        The unit cell length of the lattice in microns.
    nx_elements : float
        Number of elements along the x axis.
    ny_elements : float
        Number of elements along the y axis.
    element_dimension : float
        The dimension of a node of the lattice, it coincides with the absorber 
        side in microns.
    rotation : int, optional
        This parameter can be 1, 0 or -1. If 1 all the even rows (starting from
        the lower one) will be rotated by 180 degrees, if -1 all the odd rows 
        will be rotated by 180 degrees, if 0 no rotation will be applied.
    central_pixel_magic_number : int, optional
        1 or 0. Default is 0.

    Returns
    -------
    n : int
        Number of nodes found.
    x : list of floats
        The x coordinates of the lattice nodes in microns.
    y : list of floats
        The y coordinates of the lattice nodes in microns.
    r : list of floats
        The rotations to be applied at each node in degrees.

    '''
    n = 0
    x = []
    y = []
    r = []
    
    x_step = pitch
    y_step = pitch * np.sqrt(3)*0.5
    
    for y_i in range(ny_elements):
        for x_j in range(nx_elements-(y_i)%2):

            x.append(x_j*x_step+((y_i+central_pixel_magic_number)%2)*x_step*0.5)
            y.append(y_i*y_step)
                
            # check rotation parameter
            if rotation == 1:
                r.append(180*(y_i%2))
            elif rotation == -1:
                r.append(180*((y_i+1)%2))
            else:
                r.append(0)
            # increase the number of nodes found
            n += 1
                
    fig = plt.figure(dpi=300)
    ax0 = fig.gca()
    ax0.set_xlabel('x position [microns]')
    ax0.set_ylabel('y position [microns]')
    ax0.set_aspect('equal')
    fp = FontProperties(family='Helvetica', style='normal', weight='light')
    # draw squares
    for i, (xi, yi, ri) in enumerate(zip(x, y, r)):
        rectangle = Rectangle((xi-element_dimension*0.5, yi-element_dimension*0.5), element_dimension, element_dimension,
                              edgecolor='black', fill=False, linewidth=0.5)
        ax0.add_patch(rectangle)
        
        tp = TextPath((xi-element_dimension*0.5, yi-element_dimension*0.25), "{:d}".format(i), size=element_dimension*0.5, prop=fp)
        ax0.add_patch(PathPatch(tp, color="black"))
    
    
    ax0.set_xlim([-1000, nx_elements*x_step+1000])
    ax0.set_ylim([-1000, ny_elements*y_step+1000])
    plt.show()
    
    return n, x, y, r