import numpy as np

def get_distance_point2line(point, line):   ##  计算点到直线的距离
    """
    Args:
        point: [x0, y0]
        line: [x1, y1, x2, y2]
    """
    line_point1, line_point2 = line.boundary
    vec1 = line_point1 - point
    vec2 = line_point2 - point
    m=np.linalg.norm(line_point1 - line_point2)
    if m==0:
        print('error')
        return 0
    else:
        distance = np.abs(np.cross(vec1, vec2)) / m
    return distance