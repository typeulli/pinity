import numpy as np
import cv2

rect1 = np.array([
    [10, 10],
    [10, -10],
    [-10, -10],
    [-10, 10],
])
rect2 = np.array([
    [10, 0],
    [0, -10],
    [-10, 0],
    [0, 10],
])
rect1_pos = np.array([0, 0])
rect2_pos = np.array([15, 15])

map_ = np.zeros((80, 80, 3), dtype=np.uint8)

def draw(map_, points, pos):
    length = len(points)
    for i in range(length):
        x1, y1 = points[i] + pos + np.array([40, 40])
        x2, y2 = points[(i + 1) % length] + pos + np.array([40, 40])
        cv2.line(map_, (x1, y1), (x2, y2), (0, 255, 0), 1)
    return map_

map_ = draw(map_, rect1, rect1_pos)
map_ = draw(map_, rect2, rect2_pos)

def iscollide(rect1, rect2, rect1_pos, rect2_pos):
    pts1 = rect1 + rect1_pos
    pts2 = rect2 + rect2_pos

    def project(poly, axis):
        projs = [(p[0]*axis[0] + p[1]*axis[1]) for p in poly]
        return min(projs), max(projs)

    def overlap(minA, maxA, minB, maxB):
        return not (maxA < minB or maxB < minA)

    all_points = [pts1, pts2]
    for points in all_points:
        for i in range(len(points)):
            edge = points[(i+1) % len(points)] - points[i]
            normal = np.array([-edge[1], edge[0]], dtype=float)
            norm_len = np.linalg.norm(normal)
            if norm_len == 0:
                continue
            normal /= norm_len
            minA, maxA = project(pts1, normal)
            minB, maxB = project(pts2, normal)
            if not overlap(minA, maxA, minB, maxB):
                return False
    return True
cv2.putText(map_, iscollide(rect1, rect2, rect1_pos, rect2_pos).__str__().lower(), (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
cv2.imshow("rect1", map_)
cv2.waitKey(0)