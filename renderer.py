from typing import Annotated
import cv2
import numpy as np
from numpy.typing import NDArray
import engine
import pygame

from pathlib import Path
path_here = Path(__file__).parent.resolve()


screen = np.zeros((512, 1024, 3), dtype=np.uint8)
z_buffer = np.zeros(screen.shape[:2], dtype=np.float32)


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min(value, max_value), min_value)

    

    
                        

class SpriteRenderer(engine.Component, engine.Drawable):
    def __init__(self, gameObject: engine.GameObject) -> None:
        super().__init__(gameObject)
        self.image: cv2.typing.MatLike | None = None
        self.delta: engine.Vector3 = engine.Vector3(0, 0, 0)
    def draw(self) -> None:
        if self.image is None:
            return
        width = self.image.shape[1]
        height = self.image.shape[0]
        self.gameObject.transform.scene.show(self.image, self.gameObject.transform.position + self.delta + engine.Vector3(width, height, 0) / 2)
        
        
        
        
        
class Camera(engine.Component, engine.ScreenView):
    def __init__(self, gameObject: engine.GameObject) -> None:
        engine.Component.__init__(self, gameObject)
        engine.ScreenView.__init__(self)
        self.clearColor: tuple[int, int, int, int] = (0, 0, 0, 0)
    
        self.view = np.zeros((512, 1024, 4), dtype=np.uint8)
        self.z_buffer = np.zeros((512, 1024), dtype=np.float32)
        
        engine.SYSTEM.currentScene.view = self
    
    def worldToView(self, pos: engine.Vector3) -> engine.Vector3:
        return pos - self.gameObject.transform.position
    def viewToWorld(self, pos: engine.Vector3) -> engine.Vector3:
        return pos + self.gameObject.transform.position
    def worldToScreen(self, pos: engine.Vector3) -> engine.Vector3:
        return self.gameObject.transform.scene.viewToScreen(pos - self.gameObject.transform.position)
    def screenToWorld(self, pos: engine.Vector3) -> engine.Vector3:
        return self.gameObject.transform.scene.screenToView(pos) + self.gameObject.transform.position
        
    def render(self, surface: pygame.Surface, components: list[engine.Component]) -> None:
        if [*surface.get_size()] != [*self.view.shape[:2][::-1]]:
            self.view = np.zeros((surface.get_size()[1], surface.get_size()[0], 4), dtype=np.uint8)
            self.z_buffer = np.zeros((surface.get_size()[1], surface.get_size()[0]), dtype=np.float32)
        
        self.view[:, :] = self.clearColor
        
        self.z_buffer.fill(-float("inf"))
        
        for obj in components:
            if isinstance(obj, engine.Drawable):
                obj.draw()
    
        surface.blit(pygame.surfarray.make_surface(np.transpose(cv2.cvtColor(self.view, cv2.COLOR_BGRA2RGB), (1, 0, 2))), (0, 0)) # type: ignore
    def show(self, image: cv2.typing.MatLike, pos: engine.Vector3) -> None:
        size_image = image.shape[:2]
        size_view = self.view.shape[:2]
        
        pos = self.worldToScreen(pos) - engine.Vector3(size_image[1] / 2, size_image[0] / 2, 0)
        
        
        xleft = clamp(pos.x, 0, size_view[1])
        xright = clamp(pos.x + size_image[1], 0, size_view[1])
        ytop = clamp(pos.y, 0, size_view[0])
        ybottom = clamp(pos.y + size_image[0], 0, size_view[0])
        
        y0, x0 = int(ytop), int(xleft)
        y1, x1 = int(ybottom), int(xright)
        region_z = self.z_buffer[y0:y1, x0:x1]
        region_scr = self.view[y0:y1, x0:x1]
        region_img = image[y0 - int(pos.y):y1 - int(pos.y),
                            x0 - int(pos.x):x1 - int(pos.x)]
        alpha = region_img[..., 3] / 255.0
        alpha_mask = alpha > 0
        depth_mask = pos.z > region_z
        final_mask = alpha_mask & depth_mask

        region_z[final_mask] = pos.z
        alpha = alpha[..., np.newaxis]  # for broadcasting

        region_scr[final_mask, :3] = (
            alpha[final_mask] * region_img[final_mask, :3] +
            (1 - alpha[final_mask]) * region_scr[final_mask, :3]
        ).astype(np.uint8)

        region_scr[final_mask, 3] = (
            alpha[final_mask].squeeze() * 255 +
            (1 - alpha[final_mask].squeeze()) * region_scr[final_mask, 3]
        ).astype(np.uint8)
        

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

class Test(engine.Behaviour):
    def fixedUpdate(self) -> None:
        if engine.Input.isHold("key-100"):
            self.gameObject.transform.position += engine.Vector3.right() * engine.Time.deltaTime * 100





def start():
    pygame.init()

    surface = pygame.display.set_mode((1024, 512), pygame.SRCALPHA | pygame.DOUBLEBUF | pygame.RESIZABLE)

    pygame.display.set_caption("Renderer")

    running = True
    engine.SYSTEM.currentScene.surface = surface
    engine.SYSTEM.currentScene.start()
    while running:
        for key in list(engine.Input.keyInfo.keys()):
            if engine.Input.keyInfo[key] == engine.KeyMotion.Up:
                del engine.Input.keyInfo[key]
            elif engine.Input.keyInfo[key] == engine.KeyMotion.Down:
                engine.Input.keyInfo[key] = engine.KeyMotion.Hold
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                pass
                # TODO
            elif event.type == pygame.MOUSEMOTION:
                engine.Input.mousePosition = engine.Vector3(event.pos[0], event.pos[1])
            elif event.type == pygame.KEYDOWN:
                engine.Input.keyInfo[f"key-{event.key}"] = engine.KeyMotion.Down
            elif event.type == pygame.KEYUP:
                engine.Input.keyInfo[f"key-{event.key}"] = engine.KeyMotion.Up
            elif event.type == pygame.MOUSEBUTTONDOWN:
                keyname = engine.Input.MOUSE_BUTTON_MAP.get(event.button)
                if keyname is not None:
                    engine.Input.keyInfo[keyname] = engine.KeyMotion.Down
                else:
                    print("Unknown mouse button:", event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                keyname = engine.Input.MOUSE_BUTTON_MAP.get(event.button)
                if keyname is not None:
                    engine.Input.keyInfo[keyname] = engine.KeyMotion.Up
                else:
                    print("Unknown mouse button:", event.button)
                
        
        dofixed = engine.SYSTEM.time.update()
        engine.SYSTEM.currentScene.update()
        if dofixed:
            engine.SYSTEM.currentScene.fixedUpdate()
        engine.SYSTEM.currentScene.render(surface)
        pygame.display.flip()


if __name__ == "__main__":
    
    obj1 = engine.GameObject("obj1")
    obj1.addComponent(SpriteRenderer).image = engine.Asset.rectImage(50, 50, (0, 0, 255, 128))
    obj1.transform.position = engine.Vector3(0, 0, 0)
    obj1.addComponent(Test)


    obj2 = engine.GameObject("obj2", obj1.transform)
    obj2.transform.localPosition = engine.Vector3(25, 0, 2)
    renderer2 = obj2.addComponent(SpriteRenderer)
    renderer2.image = engine.Asset.rectImage(50, 50, (255, 0, 0, 128))


    obj3 = engine.GameObject("obj3", obj2.transform)
    obj3.transform.position = engine.Vector3(12.5, 25, 1)
    obj3.addComponent(SpriteRenderer).image = engine.Asset.rectImage(50, 50, (0, 255, 0, 128))

    camera = engine.GameObject("camera")
    camera.addComponent(Camera)

    start()