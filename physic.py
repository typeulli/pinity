from typing import Annotated
import cv2
from numpy.typing import NDArray
import numpy as np
import engine
import renderer

ColliderContour = Annotated[NDArray[np.float64], (None, 2)]
class Collider(engine.Component):
    def __init__(self, gameObject: engine.GameObject) -> None:
        super().__init__(gameObject)
        self.contour: ColliderContour | None = None

    def check(self) -> bool:
        for component in self.gameObject.transform.scene.getAllComponents():
            if isinstance(component, Collider) and component != self:
                if self.isTouch(component):
                    return True
        return False

    def isTouch(self, other: "Collider") -> bool:
        colli1 = self.contour
        colli2 = other.contour
        if colli1 is None or colli2 is None:
            return False
        
        pts1 = colli1 + self.gameObject.transform.position.asNumpy()
        pts2 = colli2 + other.gameObject.transform.position.asNumpy()
        
        def project(poly: NDArray[np.float64], axis: NDArray[np.float64]) -> tuple[float, float]:
            projs = [(p[0] * axis[0] + p[1] * axis[1]) for p in poly]
            return min(projs), max(projs)

        def overlap(minA: float, maxA: float, minB: float, maxB: float) -> bool:
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

class VisuallizeCollider(engine.Behaviour):
    def __init__(self, gameObject: "engine.GameObject"):
        super().__init__(gameObject)
        self.collider: Collider | None = None
        self.sprite: renderer.SpriteRenderer = self.gameObject.addComponent(renderer.SpriteRenderer)
        
    def update(self) -> None:
        if self.collider is None and self.gameObject.hasComponent(Collider):
            self.collider = self.gameObject.getComponent(Collider)
        if self.collider is None: return
        contour = self.collider.contour
        if contour is None: return
        
        #find x range, y range
        contour = np.array(contour)
        min_x, min_y = contour.min(axis=0)
        max_x, max_y = contour.max(axis=0)
        canvas = np.zeros((int(max_y - min_y), int(max_x - min_x), 4), dtype=np.uint8)
        cv2.polylines(canvas, [contour - [min_x, min_y]], True, (0, 255, 0, 255) if self.collider.check() else (0, 0, 255, 255), 2)

        self.sprite.delta = engine.Vector3(min_x, min_y, 0)
        self.sprite.image = canvas

class Rigidbody(engine.Component):
    def __init__(self, gameObject: engine.GameObject) -> None:
        super().__init__(gameObject)
        self.velocity: engine.Vector3 = engine.Vector3(0, 0, 0)
        self.acceleration: engine.Vector3 = engine.Vector3(0, 0, 0)
        self.mass: float = 1.0
        self.collider: Collider | None = None
        self._isGrounded: bool = False
        if self.gameObject.hasComponent(Collider):
            self.collider = self.gameObject.getComponent(Collider)

    def applyForce(self, force: engine.Vector3) -> None:
        self.acceleration += force / self.mass

    def update(self) -> None:
        if self.collider is not None and self.collider.check():
            if not self._isGrounded:
                self.velocity = engine.Vector3(0, 0, 0)  # Reset velocity on ground contact
                self.acceleration = engine.Vector3(0, 0, 0)  # Reset acceleration on ground contact
                self._isGrounded = True
                return
            self._isGrounded = True
        else:
            self._isGrounded = False
        self.gameObject.transform.position += self.velocity * engine.Time.deltaTime
        self.velocity += self.acceleration * engine.Time.deltaTime