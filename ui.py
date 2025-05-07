from typing import Callable
import cv2
import numpy as np
import engine
import pygame
import renderer

from pathlib import Path
path_here = Path(__file__).parent.resolve()





        
class Test(engine.Behaviour):
    def fixedUpdate(self) -> None:
        self.gameObject.transform.position += engine.Vector3.right() * engine.Time.deltaTime * 100

class TestFollowMouse(engine.Behaviour):
    def update(self) -> None:
        self.gameObject.transform.position = self.gameObject.transform.scene.screenToWorld(engine.Input.getMousePosition())

class VisuallizeCollider(engine.Behaviour):
    def __init__(self, gameObject: "engine.GameObject"):
        super().__init__(gameObject)
        self.collider: renderer.Collider | None = None
        self.sprite: renderer.SpriteRenderer = self.gameObject.addComponent(renderer.SpriteRenderer)
        
    def update(self) -> None:
        if self.collider is None and self.gameObject.hasComponent(renderer.Collider):
            self.collider = self.gameObject.getComponent(renderer.Collider)
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
        
class Button(engine.Behaviour):
    def __init__(self, gameObject: "engine.GameObject"):
        super().__init__(gameObject)
        self.onClick: Callable[[], None] | None = None
    
    def start(self):
        self.spriteRenderer = self.gameObject.getComponent(renderer.SpriteRenderer)
    
    def update(self):
        image = self.spriteRenderer.image
        if image is None: return
        if not engine.Input.isUp("mouse-left"): return
        
        width, height = image.shape[1], image.shape[0]
        clicked = self.gameObject.transform.scene.screenToWorld(engine.Input.getMousePosition())
        x, y = clicked.x, clicked.y
        pos = self.gameObject.transform.position
        if pos.x - width/2 <= x <= pos.x + width/2 and pos.y - height/2 <= y <= pos.y + height/2:
            if self.onClick: self.onClick()

#Label도 굳이 만들어야하나 의문

class Entry(engine.Behaviour):
    def __init__(self, gameObject: "engine.GameObject"):
        super().__init__(gameObject)
        self.focused = False
        self.text = "Entry"  # 초기 텍스트
        self.font_color = (0, 0, 0)
        self.font_scale = 1
        self.thickness = 2

    def update(self) -> None:
        # 마우스 클릭으로 포커스 판단
        clicked = self.gameObject.transform.scene.screenToWorld(engine.Input.getMousePosition())
        mx, my = clicked.x, clicked.y
        pos = self.gameObject.transform.position
        if pygame.mouse.get_pressed()[0]:
            if (pos.x <= mx <= pos.x + 200) and (pos.y <= my <= pos.y + 50):
                self.focused = True
            else:
                self.focused = False

        # 텍스트 이미지 만들기
        spriteRenderer = self.gameObject.getComponent(renderer.SpriteRenderer)
        if spriteRenderer:
            img = np.ones((50, 200, 3), dtype=np.uint8) * 255
            display_text = self.text + ("|" if self.focused else "")
            cv2.putText(img, display_text, (5, 35), cv2.FONT_HERSHEY_SIMPLEX,
                        self.font_scale, self.font_color, self.thickness)
            spriteRenderer.image = img


if __name__ == "__main__":
    camera = engine.GameObject("camera")
    camera.addComponent(renderer.Camera)
    
    coll1 = engine.GameObject("coll1")
    collider1 = coll1.addComponent(renderer.Collider)
    collider1.contour = np.array([[-50, -50], [50, -50], [50, 50], [-50, 50]])
    coll1.addComponent(VisuallizeCollider).collider = collider1
    
    coll2 = engine.GameObject("coll2")
    collider2 = coll2.addComponent(renderer.Collider)
    collider2.contour = np.array([[50, 0], [0, -50], [-50, 0], [0, 50]])
    coll2.addComponent(VisuallizeCollider).collider = collider2
    coll2.addComponent(TestFollowMouse)

    renderer.start()
