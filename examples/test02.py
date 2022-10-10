from shapely.geometry import Polygon
from shapely.ops import unary_union


poly1 = Polygon([(0,0),(1,0),(1,1),(0,1)])
poly2 = Polygon([(1,0),(2,0),(2,2),(1,2)])
poly3 = Polygon([(0,0),(-2,0),(-2,2),(0,2)])

union = unary_union([poly3,poly1,poly2])

print(list(union.exterior.coords))
