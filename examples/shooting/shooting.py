import sys
from pathlib import Path
path_here = Path(__file__).parent.resolve()
sys.path.append(str(path_here.parent.absolute()))
from engine import *
from renderer import *
from physic import *

camera = GameObject("camera")
camera.addComponent(Camera)

class BulletScript(Behaviour):
    def __init__(self, gameObject: "GameObject"):
        super().__init__(gameObject)
        self.renderer = self.gameObject.addComponent(SpriteRenderer)
        self.renderer.image = Asset.rectImage(10, 10, (0, 255, 0, 255))
        self.body = self.gameObject.addComponent(Rigidbody)
        self.body.velocity = Vector3(0, 500, 0)
        self.collider = self.gameObject.addComponent(Collider)
        self.collider.contour = np.array([[-5, -5], [5, -5], [5, 5], [-5, 5]])

    def update(self) -> None:
        if self.collider.check():
            self.renderer.image = None
            self.body.velocity = Vector3(0, 0, 0)
    


class PlayerScript(Behaviour):
    def __init__(self, gameObject: "GameObject"):
        super().__init__(gameObject)
        self.renderer: SpriteRenderer = self.gameObject.addComponent(SpriteRenderer)
        self.body: Rigidbody = self.gameObject.addComponent(Rigidbody)
        self.body.mass = 1.0
        
        self.cooltime = 0.0
        self.available = True

    def update(self) -> None:
        if Input.isHold("key-100"):  # key d
            self.body.velocity.x = 500
        elif Input.isHold("key-97"):  # key a
            self.body.velocity.x = -500
        else:
            self.body.velocity.x = 0
        
        self.cooltime -= Time.deltaTime
        if self.cooltime < 0:
            self.available = True
            
        
        if self.available and Input.isHold("key-119"):
            self.cooltime = 0.5
            self.available = False
            bullet = GameObject("bullet")
            bullet.transform.position = self.gameObject.transform.position + Vector3(0, 20, 0)
            bullet.addComponent(BulletScript)

player = GameObject("player")
player.transform.position = Vector3(0, -200, 0)
player.addComponent(SpriteRenderer).image = Asset.rectImage(50, 50, (255, 0, 0, 128))
player.addComponent(PlayerScript)


class EnemyScript(Behaviour):
    def __init__(self, gameObject: "GameObject"):
        super().__init__(gameObject)
        self.collider: Collider = self.gameObject.addComponent(Collider)
        self.collider.contour = np.array([[-25, -25], [25, -25], [25, 25], [-25, 25]])
        self.renderer: SpriteRenderer = self.gameObject.addComponent(SpriteRenderer)
        self.renderer.image = Asset.rectImage(50, 50, (0, 0, 255, 128))
    def update(self) -> None:
        if self.collider.check():
            self.renderer.image = None
            self.collider.contour = None
            

for i in range(5):
    for j in range(4 - i):
        enemy = GameObject(f"enemy_{i}_{j}")
        x_offset = (j - (3 - i) / 2) * 60  # Adjust spacing between enemies
        y_offset = i * -60  # Adjust vertical spacing
        enemy.transform.position = Vector3(x_offset, y_offset, 0) + Vector3(0, 200, 0)
        enemy.addComponent(EnemyScript)

start()