from abc import ABCMeta, abstractmethod
from enum import Enum
import time
from typing import Annotated, Any, TypeVar
from pathlib import Path
import cv2
import numpy as np
from numpy.typing import NDArray
import pygame


class _Asset:
    """
    A utility class for managing and processing image assets.
    """
    def __init__(self, path: Path):
        """
        Initializes the Asset manager with a given path.
        :param path: The directory path where assets are stored.
        """
        self.path = path
    def loadImage(self, path: str) -> cv2.typing.MatLike:
        """
        Loads an image from the specified path.
        :param path: The relative path to the image file.
        :return: The loaded image as a numpy array.
        """
        image = cv2.imdecode(np.fromfile(str(self.path / path), dtype=np.uint8), cv2.IMREAD_COLOR | cv2.IMREAD_UNCHANGED)
        if image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        return image
    def rectImage(self, width: int, height: int, color: tuple[int, int, int, int] = (255, 255, 255, 255)) -> cv2.typing.MatLike:
        """
        Creates a solid color rectangle image.
        :param width: The width of the rectangle.
        :param height: The height of the rectangle.
        :param color: The color of the rectangle in RGBA format.
        :return: A numpy array representing the rectangle image.
        """
        mat = np.zeros((height, width, 4), dtype=np.uint8)
        mat[:, :] = color
        return mat
    def splitTileMap(self, image: cv2.typing.MatLike, tileWidth: int = 32, tileHeight: int = 32, gapX: int = 0, gapY: int = 0, offsetX: int = 0, offsetY: int = 0) -> list[list[cv2.typing.MatLike]]:
        """
        Splits a tile map image into smaller tiles.
        :param image: The tile map image to split.
        :param tileWidth: The width of each tile.
        :param tileHeight: The height of each tile.
        :param gapX: The horizontal gap between tiles.
        :param gapY: The vertical gap between tiles.
        :param offsetX: The horizontal offset to start splitting.
        :param offsetY: The vertical offset to start splitting.
        :return: A list of lists containing the split tiles.
        """
        tiles: list[list[cv2.typing.MatLike]] = []
        for y in range(offsetY, image.shape[0], tileHeight + gapY):
            tiles.append([
                image[y:y + tileHeight, x:x + tileWidth] for x in range(offsetX, image.shape[1], tileWidth + gapX)
            ])
        return tiles
Asset = _Asset(Path(__file__).parent.resolve())



class Vector3:
    def __init__(self, x: float, y: float, z: float=0):
        """
        Initializes a 3D vector with x, y, and z coordinates.
        :param x: The x coordinate of the vector.
        :param y: The y coordinate of the vector.
        :param z: The z coordinate of the vector (default is 0).
        """
        self.x = x
        self.y = y
        self.z = z
    
    def asNumpy(self) -> Annotated[NDArray[np.float64], (2,)]:
        """
        Converts the vector to a numpy array with shape (2,).
        """
        return np.array([self.x, self.y], dtype=np.float64)
    def __add__(self, other: "Vector3") -> "Vector3":
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other: "Vector3") -> "Vector3":
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    def __mul__(self, scalar: float) -> "Vector3":
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    def __truediv__(self, scalar: float) -> "Vector3":
        if scalar == 0:
            raise ZeroDivisionError("Division by zero")
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)
    def __neg__(self) -> "Vector3":
        return Vector3(-self.x, -self.y, -self.z)
    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"
    def __repr__(self):
        return f"Vector3({self.x}, {self.y}, {self.z})"
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Vector3) == Vector3 and self.x == other.x and self.y == other.y and self.z == other.z
    
    @property
    def normalized(self) -> "Vector3":
        """
        Returns a normalized version of the vector.
        """
        length = (self.x**2 + self.y**2) ** 0.5
        if length == 0:
            return Vector3(0, 0, 0)
        return Vector3(self.x / length, self.y / length, self.z)

    @classmethod
    def one  (cls) -> "Vector3": return Vector3(1, 1, 0)
    @classmethod
    def zero (cls) -> "Vector3": return Vector3(0, 0, 0)
    @classmethod
    def up   (cls) -> "Vector3": return Vector3(0, 1, 0)
    @classmethod
    def down (cls) -> "Vector3": return Vector3(0, -1, 0)
    @classmethod
    def left (cls) -> "Vector3": return Vector3(-1, 0, 0)
    @classmethod
    def right(cls) -> "Vector3": return Vector3(1, 0, 0)
    
    
class Positionable:
    def __init__(self, position: Vector3 | None = None, rotation: float | None = None, scale: Vector3 | None = None):
        """
        Initializes a Positionable object with local position, rotation, and scale.
        :param position: The local position of the object (default is Vector3.zero()).
        :param rotation: The local rotation of the object in degrees (default is 0.0).
        :param scale: The local scale of the object (default is Vector3.one()).
        """
        self.localPosition = position if position else Vector3.zero()
        self.rotation = rotation if rotation else 0.0
        self.scale = scale if scale else Vector3.one()
        
        self._children: list[Transform] = []
    @property
    def parent(self) -> "Positionable":
        raise NotImplementedError("Cannot get parent of Positionable.")
    @parent.setter
    def parent(self, value: "Positionable") -> None:
        raise NotImplementedError("Cannot set parent of Positionable.")
    
    @property
    def position(self) -> Vector3:
        raise NotImplementedError("Cannot get position of Positionable.")
    @position.setter
    def position(self, value: Vector3) -> None:
        raise NotImplementedError("Cannot set position of Positionable.")
    
    @property
    def children(self) -> list["Transform"]:
        return self._children
class SceneTransform(Positionable):
    def __init__(self, scene: "Scene"):
        """
        Initializes a SceneTransform object that represents the root transform of a Scene.
        """
        super().__init__()
        self._scene = scene
    
    @property
    def scene(self) -> "Scene":
        return self._scene
    
    @property
    def position(self) -> Vector3:
        return self.localPosition
    @position.setter
    def position(self, value: Vector3) -> None:
        raise AttributeError("Cannot set position of SceneTransform.")
class Scene:
    def __init__(self): 
        """
        Initializes a Scene object with a root transform and a view.
        """
        self.transform = SceneTransform(self)
        self.view: ScreenView | None = None
        self.surface: pygame.Surface | None = None
    
    def screenToView(self, pos: Vector3) -> Vector3:
        """
        Converts screen coordinates to view coordinates.
        :param pos: The screen coordinates to convert.
        :return: The converted view coordinates.
        """
        if self.surface:
            x = pos.x - (self.surface.get_size()[0] >> 1)
            y = -pos.y + (self.surface.get_size()[1] >> 1)
            return Vector3(x, y, pos.z)
        raise AttributeError("Scene surface is not set.")
    def viewToScreen(self, pos: Vector3) -> Vector3:
        """
        Converts view coordinates to screen coordinates.
        :param pos: The view coordinates to convert.
        :return: The converted screen coordinates.
        """
        if self.surface:
            x = pos.x + (self.surface.get_size()[0] >> 1)
            y = -pos.y + (self.surface.get_size()[1] >> 1)
            return Vector3(x, y, pos.z)
        raise AttributeError("Scene surface is not set.")
    def screenToWorld(self, pos: Vector3) -> Vector3:
        """
        Converts screen coordinates to world coordinates.
        :param pos: The screen coordinates to convert.
        :return: The converted world coordinates.
        """
        if self.view:
            return self.view.screenToWorld(pos)
        raise AttributeError("Scene view is not set.")
    def worldToScreen(self, pos: Vector3) -> Vector3:
        """
        Converts world coordinates to screen coordinates.
        :param pos: The world coordinates to convert.
        :return: The converted screen coordinates.
        """
        if self.view:
            return self.view.worldToScreen(pos)
        raise AttributeError("Scene view is not set.")
    def worldToView(self, pos: Vector3) -> Vector3:
        """
        Converts world coordinates to view coordinates.
        :param pos: The world coordinates to convert.
        :return: The converted view coordinates.
        """
        if self.view:
            return self.view.worldToView(pos)
        raise AttributeError("Scene view is not set.")
    def viewToWorld(self, pos: Vector3) -> Vector3:
        """
        Converts view coordinates to world coordinates.
        :param pos: The view coordinates to convert.
        :return: The converted world coordinates.
        """
        if self.view:
            return self.view.viewToWorld(pos)
        raise AttributeError("Scene view is not set.")
    
    
    def show(self, image: cv2.typing.MatLike, pos: Vector3) -> None:
        """
        Displays an image at a specified position in the scene.
        :param image: The image to display.
        :param pos: The position in world coordinates where the image should be displayed.
        :return: None
        """
        if self.view:
            self.view.show(image, pos)
        else:
            print("WARN : No view set for scene.")
    def render(self, surface: pygame.Surface) -> None:
        """
        Renders the scene to a specified surface.
        :param surface: The pygame surface to render the scene onto.
        :return: None
        """
        if self.view:
            self.view.render(surface, self.getAllComponents())
    def getAllComponents(self) -> list["Component"]:
        """
        Collects all components in the scene, sorted by their defined order in SYSTEM.orders.
        :return: A list of all components in the scene, sorted by their order.
        """
        
        components: dict[type[Component], list[Component]] = {key: [] for key in SYSTEM.orders.keys()}
        
        
        queue: list[Transform] = [transform for transform in self.transform.children if transform.gameObject.active]
        while queue:
            current = queue.pop(0)
            for c in current.children:
                if c.gameObject.active:
                    queue.append(c)
            for component in current.gameObject.components:
                components[type(component)].append(component)
        

        results: list[Component] = []
        for type_, _ in sorted(SYSTEM.orders.items(), key=lambda x: x[1]):
                results.extend(components[type_])
                
        
        return results
    def start(self) -> None:
        """
        Starts all components in the scene.
        """
        for component in self.getAllComponents():
            component.start()
    def update(self) -> None:
        """
        Updates all components in the scene.
        """
        for component in self.getAllComponents():
            component.update()
    def fixedUpdate(self) -> None:
        """
        Fixed update for all components in the scene.
        """
        for component in self.getAllComponents():
            component.fixedUpdate()

class _Time:
    def __init__(self):
        self.__lastUpdate = 0.0
        self.__nextFixedUpdate = 0.01
        self.__deltaTime = 0.0
        self.fixedScale = 0.0
    
    
    
    @property
    def deltaTime(self) -> float: 
        return self.__deltaTime
    @property
    def lastUpdate(self) -> float:
        return self.__lastUpdate
    
    def start(self) -> None:
        self.__lastUpdate = time.time()
        self.__nextFixedUpdate = self.__lastUpdate + self.fixedScale
    def update(self) -> bool:
        now = time.time()
        self.__deltaTime = now - self.__lastUpdate
        self.__lastUpdate = now
        if now >= self.__nextFixedUpdate:
            self.__nextFixedUpdate += self.fixedScale
            return True
        return False

class KeyMotion(Enum):
    Idle = 0
    Down = 1
    Hold = 2
    Up = 3

class _Input:
    MOUSE_BUTTON_MAP = {
        1: "mouse-left",
        2: "mouse-middle",
        3: "mouse-right",
        4: "mouse-fn1",
        5: "mouse-fn2",
        6: "mouse-fn3",
    }
    
    def __init__(self):
        self.mousePosition = Vector3.zero()
        self.keyInfo: dict[str, KeyMotion] = {}
    def isDown(self, key: str) -> bool:
        return self.keyInfo.get(key, KeyMotion.Idle) == KeyMotion.Down
    def isHold(self, key: str) -> bool:
        return self.keyInfo.get(key, KeyMotion.Idle) == KeyMotion.Hold
    def isUp(self, key: str) -> bool:
        return self.keyInfo.get(key, KeyMotion.Idle) == KeyMotion.Up
    def getMousePosition(self) -> Vector3:
        return Vector3(*pygame.mouse.get_pos())

class System:
    def __init__(self):
        self.currentScene = Scene()
        self.time = _Time()
        self.time.update()
        
        self.input = _Input()
        
        self.orders: dict[type[Component], int] = {}
SYSTEM = System()
Time = SYSTEM.time
Input = SYSTEM.input

class Component(metaclass=ABCMeta):
    def __init__(self, gameObject: "GameObject"):
        self.gameObject = gameObject
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        SYSTEM.orders[cls] = 0
    
    def start(self) -> None: ...
    def update(self) -> None: ...
    def fixedUpdate(self) -> None: ...


class Drawable(metaclass=ABCMeta):
    @abstractmethod
    def draw(self) -> None:
        raise NotImplementedError("Subclasses must implement draw method")
    
class ScreenView(metaclass=ABCMeta):
    @abstractmethod
    def worldToView(self, pos: Vector3) -> Vector3:
        raise NotImplementedError("Subclasses must implement worldToView method")
    @abstractmethod
    def viewToWorld(self, pos: Vector3) -> Vector3:
        raise NotImplementedError("Subclasses must implement viewToWorld method")
    @abstractmethod
    def worldToScreen(self, pos: Vector3) -> Vector3:
        raise NotImplementedError("Subclasses must implement viewToScreen method")
    @abstractmethod
    def screenToWorld(self, pos: Vector3) -> Vector3:
        raise NotImplementedError("Subclasses must implement screenToWorld method")
    @abstractmethod
    def render(self, surface: pygame.Surface, components: list[Component]) -> None:
        raise NotImplementedError("Subclasses must implement render method")
    @abstractmethod
    def show(self, image: cv2.typing.MatLike, pos: Vector3) -> None:
        raise NotImplementedError("Subclasses must implement show method")

class Behaviour(Component):
    def __init__(self, gameObject: "GameObject"):
        super().__init__(gameObject)
        self.enabled = True
    def start(self) -> None:
        if self.enabled:
            super().start()
    def update(self) -> None:
        if self.enabled:
            super().update()
    def fixedUpdate(self) -> None:
        if self.enabled:
            super().fixedUpdate()


class UniqueComponent(Component):
    def __init__(self, gameObject: "GameObject"):
        super().__init__(gameObject)
        if gameObject.hasComponent(self.__class__):
            raise TypeError(f"GameObject {gameObject.name} already has a component of type {self.__class__.__name__}.")

        
class Transform(UniqueComponent, Positionable):
    def __init__(self, gameObject: "GameObject", parent: "Positionable", position: Vector3 | None = None, rotation: float | None = None, scale: Vector3 | None = None):
        UniqueComponent.__init__(self, gameObject)
        Positionable.__init__(self, position, rotation, scale)
        self._parent = parent
        parent._children.append(self)
    
    @property
    def parent(self) -> "Positionable":
        return self._parent
    @parent.setter
    def parent(self, value: "Positionable") -> None:
        if self._parent is not value:
            self._parent._children.remove(self)
            value._children.append(self)
            self._parent = value
    @property
    def scene(self) -> Scene:
        parent = self._parent
        while True:
            if isinstance(parent, SceneTransform):
                return parent.scene
            parent = parent.parent
    
    @property
    def position(self) -> Vector3:
        return self.localPosition + self._parent.position
    @position.setter
    def position(self, value: Vector3) -> None:
        self.localPosition = value - self._parent.position

T = TypeVar("T", bound=Component)
class GameObject:
    def __init__(self, name: str = "GameObject", parent: "Transform | None" = None):
        self.name = name
        self.tags: list[str] = []
        self.active = True
        self.components: list[Component] = []
        
        self.transform: Transform = Transform(self, parent if parent else SYSTEM.currentScene.transform, Vector3.zero(), 0.0, Vector3.one())
        self.components.append(self.transform)
    def addComponent(self, component: type[T]) -> T:
        new_component = component(self)
        self.components.append(new_component)
        return new_component
    def getComponent(self, component: type[T]) -> T:
        for c in self.components:
            if isinstance(c, component):
                return c
        raise TypeError(f"Component {component.__name__} not found in {self.name}.")
    def getComponents(self, component: type[T]) -> list[T]:
        return [c for c in self.components if isinstance(c, component)]
    def hasComponent(self, component: type[T]) -> bool:
        for c in self.components:
            if isinstance(c, component):
                return True
        return False
    def invoke(self, method: str, *args: Any, **kwargs: Any) -> None:
        for c in self.components:
            if hasattr(c, method):
                getattr(c, method)(*args, **kwargs)


def test_position():
    obj = GameObject("TestObject")
    obj2 = GameObject("TestObject2", obj.transform)
    obj.transform.position = Vector3(1, 1, 0)
    print(obj2.transform.position)

def test_clock():
    clock = _Time()
    clock.fixedScale = 1
    startTime = time.time()
    clock.start()
    while True:
        print(f"\r{time.time() - startTime:.4f} {clock.deltaTime:.4f}", end="")
        if clock.update():
            print("Fixed Update", end="")
        print("                          ", end="")
        [3 + 5 for _ in range(1000000)]
if __name__ == "__main__":
    test_position()
    test_clock()