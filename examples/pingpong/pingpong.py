import sys
from pathlib import Path
path_here = Path(__file__).parent.resolve()
sys.path.append(str(path_here.parent.parent.absolute()))
from engine import *
from renderer import *
from physic import *
import numpy as np

class EnemyScript(Behaviour):
    def __init__(self, gameObject: "GameObject"):
        super().__init__(gameObject)
        self.collider: Collider = self.gameObject.addComponent(Collider)
        self.collider.contour = np.array([[-5, -5], [5, -5], [5, 5], [-5, 5]])
        self.vx = 100
        self.vy = 100
    def update(self) -> None:
        if self.collider.check():
            self.vx = -self.vx
            self.vy = -self.vy

class PingPongBoardScript(Behaviour):
    def __init__(self, gameObject: "GameObject"):
        super().__init__(gameObject)
        self.renderer: SpriteRenderer = self.gameObject.addComponent(SpriteRenderer)
        self.renderer.image = Asset.rectImage(20, 60, (255, 255, 255, 255))
        self.collider: Collider = self.gameObject.addComponent(Collider)
        self.collider.contour = np.array([[-10, -30], [10, -30], [10, 30], [-10, 30]])
        self.collider.isTrigger = True
        self.keyup = ""
        self.keydown = ""
    def update(self) -> None:
        if self.keyup:
            if Input.isHold(f"key-{ord(self.keyup)}"):
                self.gameObject.transform.position += Vector3(0, 1, 0) * Time.deltaTime * 400
        if self.keydown:
            if Input.isHold(f"key-{ord(self.keydown)}"):
                self.gameObject.transform.position += Vector3(0, -1, 0) * Time.deltaTime * 400


camera = GameObject("camera")
camera.addComponent(Camera)


board1 = GameObject("board1")
board1.transform.position = Vector3(-300, 0, 0)
script1 = board1.addComponent(PingPongBoardScript)
script1.keyup = "w"
script1.keydown = "s"

board2 = GameObject("board2")
board2.transform.position = Vector3(300, 0, 0)
script2 = board2.addComponent(PingPongBoardScript)
script2.keyup = "i"
script2.keydown = "j"

class BallScript(Behaviour):
    def __init__(self, gameObject: "GameObject"):
        super().__init__(gameObject)
        self.collider: Collider = self.gameObject.addComponent(Collider)
        self.collider.contour = np.array([[-5, -5], [5, -5], [5, 5], [-5, 5]])
        self.collider.isTrigger = True
        self.body: Rigidbody = self.gameObject.addComponent(Rigidbody)
        self.body.velocity = Vector3(200, 100, 0)
        
    def update(self) -> None:
        if self.collider.isTouch(board1.getComponent(Collider)) or self.collider.isTouch(board2.getComponent(Collider)):
            self.body.velocity.x = -self.body.velocity.x
            self.gameObject.transform.position.x += self.body.velocity.x * 0.01
        
        if self.gameObject.transform.position.y < -250:
            self.body.velocity.y = 100
        if self.gameObject.transform.position.y > 250:
            self.body.velocity.y = -100

ball = GameObject("ball")
ball.addComponent(SpriteRenderer).image = Asset.rectImage(10, 10, (0, 0, 255, 255))
ball.addComponent(BallScript)

border = GameObject("border")
border.transform.position = Vector3(0, 0, 0)
border.addComponent(Collider).contour = np.array([[-400, -250], [400, -250], [400, 250], [-400, 250]])
border.addComponent(VisuallizeCollider)

start()