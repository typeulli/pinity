import sys
from pathlib import Path
path_here = Path(__file__).parent.resolve()
sys.path.append(str(path_here.parent.parent.absolute()))
from engine import *
from renderer import *
from physic import *

class PingPongBoardScript(Behaviour):
    def __init__(self, gameObject: "GameObject"):
        super().__init__(gameObject)
        self.renderer: SpriteRenderer = self.gameObject.addComponent(SpriteRenderer)
        self.renderer.image = Asset.rectImage(20, 60, (255, 255, 255, 255))
        self.keyup = ""
        self.keydown = ""
    def update(self) -> None:
        if self.keyup:
            if Input.isHold(f"key-{ord(self.keyup)}"):
                self.gameObject.transform.position += Vector3(0, 1, 0) * Time.deltaTime * 100
        if self.keydown:
            if Input.isHold(f"key-{ord(self.keydown)}"):
                self.gameObject.transform.position += Vector3(0, -1, 0) * Time.deltaTime * 100


camera = GameObject("camera")
camera.addComponent(Camera)


baord1 = GameObject("board1")
baord1.transform.position = Vector3(-200, 0, 0)
baord1.addComponent(PingPongBoardScript).keyup = "w"
baord1.addComponent(PingPongBoardScript).keydown = "s"



start()