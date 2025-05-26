from engine import *
from renderer import *
from physic import *

mode: int = 3

if mode == 1:
    
    class Test1(engine.Behaviour):
        def fixedUpdate(self) -> None:
            if engine.Input.isHold("key-100"):
                self.gameObject.transform.position += engine.Vector3.right() * engine.Time.deltaTime * 100

    obj1 = engine.GameObject("obj1")
    obj1.addComponent(SpriteRenderer).image = engine.Asset.rectImage(50, 50, (0, 0, 255, 128))
    obj1.transform.position = engine.Vector3(0, 0, 0)
    obj1.addComponent(Test1)


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
    
elif mode == 2:
    class TestFollowMouse(engine.Behaviour):
        def update(self) -> None:
            self.gameObject.transform.position = self.gameObject.transform.scene.screenToWorld(engine.Input.getMousePosition())

    camera = engine.GameObject("camera")
    camera.addComponent(Camera)
    
    coll1 = engine.GameObject("coll1")
    collider1 = coll1.addComponent(Collider)
    collider1.contour = np.array([[-50, -50], [50, -50], [50, 50], [-50, 50]])
    coll1.addComponent(VisuallizeCollider).collider = collider1
    
    coll2 = engine.GameObject("coll2")
    collider2 = coll2.addComponent(Collider)
    collider2.contour = np.array([[50, 0], [0, -50], [-50, 0], [0, 50]])
    coll2.addComponent(VisuallizeCollider).collider = collider2
    coll2.addComponent(TestFollowMouse)

    start()

elif mode == 3:
    
    camera = engine.GameObject("camera")
    camera.addComponent(Camera)
    camera.addComponent(Debugger)
    
    coll1 = engine.GameObject("coll1")
    collider1 = coll1.addComponent(Collider)
    collider1.contour = np.array([[-10, -10], [10, -10], [10, 10], [-10, 10]])
    coll1.addComponent(VisuallizeCollider).collider = collider1
    coll1.transform.position = engine.Vector3(0, -200, 0)
    
    coll2 = engine.GameObject("coll2")
    collider2 = coll2.addComponent(Collider)
    collider2.contour = np.array([[-10, -10], [10, -10], [10, 10], [-10, 10]])
    coll2.addComponent(VisuallizeCollider).collider = collider2
    coll2.transform.position = engine.Vector3(0, 200, 0)
    
    class Jump(engine.Behaviour):
        def update(self) -> None:
            if engine.Input.isDown("key-83") or engine.Input.isDown("key-115"):
                self.gameObject.addComponent(Rigidbody).acceleration = engine.Vector3(0, -100, 0)
            if engine.Input.isDown("key-32"):
                if self.gameObject.hasComponent(Rigidbody):
                    self.gameObject.getComponent(Rigidbody).velocity += engine.Vector3(0, 100, 0)
                    self.gameObject.getComponent(Rigidbody).acceleration = engine.Vector3(0, -100, 0)
    coll2.addComponent(Jump)
    
    start()