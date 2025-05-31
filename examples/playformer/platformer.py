# TODO Copyright ⓒ 2021 Goldmeta
import sys
from pathlib import Path
path_here = Path(__file__).parent.resolve()
sys.path.append(str(path_here.parent.absolute()))
from engine import *
from renderer import *
from physic import *


path_platformer = path_here / "assets" / "Simple 2D Platformer BE2"
image_player_grid = Asset.splitTileMap(Asset.loadImage(str(path_platformer / "Sprites" / "Player.png")), 16, 16, 1, 1)
image_player1_right = cv2.resize(image_player_grid[0][0], (64, 64), interpolation=cv2.INTER_NEAREST)
image_player2_right = cv2.resize(image_player_grid[0][1], (64, 64), interpolation=cv2.INTER_NEAREST)
image_player1_left = cv2.flip(image_player1_right, 1)
image_player2_left = cv2.flip(image_player2_right, 1)

player = GameObject("player")
class PlayerScript(Behaviour):
    def __init__(self, gameObject: "GameObject"):
        super().__init__(gameObject)
        self.direction = 1
        self.mode = 0
        self.dt = .0
        self.renderer: SpriteRenderer = self.gameObject.addComponent(SpriteRenderer)
        self.body: Rigidbody = self.gameObject.addComponent(Rigidbody)
        self.body.mass = 1.0
        self.body.acceleration = engine.Vector3(0, -100, 0)

        self.gravity = 400
    def update(self) -> None:
        self.dt += Time.deltaTime
        if self.dt > 0.4:
            self.dt -= 0.4
            self.mode = (self.mode + 1) % 2

        if self.mode == 0:
            self.renderer.image = image_player1_right if self.direction == 1 else image_player1_left
        else:
            self.renderer.image = image_player2_right if self.direction == 1 else image_player2_left

        if engine.Input.isHold("key-119"):  # key w
            self.gravity = 0

        if self.body.acceleration.x != 0:
            if self.direction == 0 and self.body.velocity.x > 0:
                self.body.acceleration.x = 0
                self.body.velocity.x = 0
                return
            if self.direction == 1 and self.body.velocity.x < 0:
                self.body.acceleration.x = 0
                self.body.velocity.x = 0
                return
                
            if self.body.acceleration.x > 0:
                self.body.acceleration.x -= 10 * Time.deltaTime
            else:
                self.body.acceleration.x += 10 * Time.deltaTime
        
        # key a
        if engine.Input.isHold("key-97"):
            self.direction = 0
            self.gameObject.transform.position.y += self.gravity / 40
            self.body.velocity.x = -200
            self.body.acceleration = engine.Vector3(200, -self.gravity, 0)
        # key d
        if engine.Input.isHold("key-100"):
            self.direction = 1
            self.gameObject.transform.position.y += self.gravity / 40
            self.body.velocity.x = 200
            self.body.acceleration = engine.Vector3(-200, -self.gravity, 0)
        if engine.Input.isDown("key-32"):
            self.body.velocity += engine.Vector3(0, self.gravity, 0)
            self.body.acceleration = engine.Vector3(0, -self.gravity, 0)
player.transform.position = Vector3(-300, -40, 100)
player.addComponent(Collider).contour = np.array([[-25, -25], [25, -25], [25, 25], [-25, 25]])
player.addComponent(PlayerScript)



camera = GameObject("camera")
camera.addComponent(Camera).clearColor = (235, 206, 135, 255)  # Sky blue color
camera.transform.parent = player.transform

# icon = Asset.loadImage(str(path_platformer / "App Icon.png"))
# icon = cv2.resize(icon, (32, 32), interpolation=cv2.INTER_AREA)
tiles = Asset.splitTileMap(Asset.loadImage(str(path_platformer / "Sprites" / "Platforms.png")), 16, 16, 1, 1)

# obj_copyright_icon = GameObject("copyright_icon")
# obj_copyright_icon.addComponent(SpriteRenderer).image = icon
# obj_copyright_icon.transform.position = Vector3(-220, -240, 0)

image_sky = Asset.loadImage(str(path_here / "assets" / "sky.png"))
class ResizeSky(Behaviour):
    def fixedUpdate(self) -> None:
        surface = SYSTEM.currentScene.surface
        if surface is None: return
        campos = camera.transform.position
        campos.z = -10
        self.gameObject.transform.position = campos
obj_sky = GameObject("sky")
# obj_sky.addComponent(SpriteRenderer).image = cv2.resize(image_sky, (1024, 812), interpolation=cv2.INTER_AREA)
# obj_sky.addComponent(ResizeSky)


MAP = [
    [0, 0, 0, 0, 0, 0, 13, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
    [0, 0, 0, 13, 5, 5, 15, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8],
    [4, 5, 5, 15, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8],
    [10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11],
]

tileindex = {x+3*y+1: (x, y) for y in range(len(tiles)) for x in range(len(tiles[y]))}
pos_delta = Vector3(-400, 0, 0)
for x in range(len(MAP)):
    for y in range(len(MAP[x])):
        if MAP[x][y] == 0: continue
        obj = GameObject(f"tile_{x}_{y}")
        tile_x, tile_y = tileindex[MAP[x][y]]
        obj.addComponent(SpriteRenderer).image = cv2.resize(tiles[tile_y][tile_x], (64, 64), interpolation=cv2.INTER_NEAREST)
        obj.transform.position = Vector3(y * 64, -x * 64, 0) + pos_delta
        obj.addComponent(Collider).contour = np.array([[-32, -32], [32, -32], [32, 32], [-32, 32]])

image_coin_grid = [
    cv2.resize(image, (64, 64), interpolation=cv2.INTER_NEAREST)
    for image in Asset.splitTileMap(Asset.loadImage(str(path_platformer / "Sprites" / "Coins.png")), 16, 16, 1, 1)[-1]
]
class CoinScript(Behaviour):
    def __init__(self, gameObject: "GameObject"):
        super().__init__(gameObject)
        self.mode = 0
        self.dt = .0
        self.renderer: SpriteRenderer = self.gameObject.addComponent(SpriteRenderer)
        self.collider: Collider = self.gameObject.addComponent(Collider)
        self.collider.isTrigger = True
        self.collider.contour = np.array([[-32, -32], [32, -32], [32, 32], [-32, 32]])
        self.exist = True
    def update(self) -> None:
        if not self.exist: return
        self.dt += Time.deltaTime
        if self.dt > 0.2:
            self.dt -= 0.2
            self.mode = (self.mode + 1) % len(image_coin_grid)
        self.renderer.image = image_coin_grid[self.mode]
        if self.collider.isTouch(player.getComponent(Collider)):
            self.renderer.image = None
            self.exist = False
coin1 = GameObject("coin1")
coin1.transform.position = Vector3(-140, 50, 50)
coin1.addComponent(CoinScript)

coin2 = GameObject("coin2")
coin2.transform.position = Vector3(-20, 160, 50)
coin2.addComponent(CoinScript)
coin3 = GameObject("coin3")

start()