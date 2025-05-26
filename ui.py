from typing import Callable
import cv2
import numpy as np
import engine
import pygame
import renderer

from pathlib import Path
path_here = Path(__file__).parent.resolve()





        
        
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


