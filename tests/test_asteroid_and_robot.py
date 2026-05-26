from src.asteroid import Asteroid
from src.robot import Robot, Direction


def test_asteroid_is_dataclass():
    """
    Verifies that Asteroid uses dataclass field generation.
    This keeps the data model lightweight while still giving the object explicit
    named attributes for the grid size.
    """
    assert hasattr(Asteroid, "__dataclass_fields__"), "Asteroid should be a dataclass"


def test_asteroid_bounds():
    """
    Verifies inclusive asteroid boundary checks.
    The assertions cover the origin, the maximum x/y coordinates, and values
    just outside the accepted grid.
    """
    asteroid = Asteroid.from_dict({"x": 5, "y": 5})
    assert asteroid.is_within_bounds(0, 0)
    assert asteroid.is_within_bounds(5, 5)
    assert not asteroid.is_within_bounds(6, 0)
    assert not asteroid.is_within_bounds(0, 6)


def test_robot_turning():
    """
    Verifies robot bearing changes through left and right turns.
    The test starts north, turns left to west, then performs a full clockwise
    rotation to prove the direction sequence wraps correctly.
    """
    asteroid = Asteroid.from_dict({"x": 5, "y": 5})
    robot = Robot({"x": 1, "y": 2}, "north", asteroid)
    robot.turn_left()
    assert robot.bearing == Direction.WEST
    robot.turn_right()
    robot.turn_right()
    robot.turn_right()
    robot.turn_right()
    assert robot.bearing == Direction.WEST


def test_robot_move_forward_within_bounds():
    """
    Verifies normal forward movement without crossing a boundary.
    A north-facing robot should keep the same x coordinate and increment y.
    """
    asteroid = Asteroid.from_dict({"x": 5, "y": 5})
    robot = Robot({"x": 1, "y": 2}, "north", asteroid)
    robot.move_forward()
    assert robot.x == 1 and robot.y == 3


def test_robot_move_forward_out_of_bounds():
    """
    Verifies north-edge wrap-around movement.
    A robot moving north from the maximum y coordinate should reappear at y=0.
    """
    asteroid = Asteroid.from_dict({"x": 5, "y": 5})
    robot = Robot({"x": 1, "y": 5}, "north", asteroid)
    robot.move_forward()
    assert robot.x == 1 and robot.y == 0, f"Expected wrap-around to (1,0), got ({robot.x},{robot.y})"


def test_robot_current_state():
    """
    Verifies the public robot state representation.
    The returned named tuple is converted to a dictionary so the values can be
    compared with the expected JSON-friendly shape.
    """
    asteroid = Asteroid.from_dict({"x": 5, "y": 5})
    robot = Robot({"x": 2, "y": 3}, "east", asteroid)
    state = robot.current_state()
    expected = {"x": 2, "y": 3, "bearing": "east"}
    assert state._asdict() == expected, f"Expected {expected}, got {state._asdict()}"


def test_robot_state_instance():
    """
    Verifies that current_state returns the RobotState named tuple type.
    The test checks both the concrete type and the serialisable field values.
    """
    asteroid = Asteroid.from_dict({"x": 5, "y": 5})
    robot = Robot({"x": 1, "y": 1}, "south", asteroid)
    state = robot.current_state()
    from src.robot import RobotState
    assert isinstance(state, RobotState), "current_state should return a RobotState instance"
    expected = {"x": 1, "y": 1, "bearing": "south"}
    assert state._asdict() == expected, f"Expected {expected}, got {state._asdict()}"


def test_direct_robot_state_namedtuple():
    """
    Verifies RobotState field access and tuple behaviour directly.
    The test checks named attributes and unpacking so later output code can rely
    on both forms safely.
    """
    from src.robot import RobotState
    state = RobotState(x=10, y=20, bearing="north")
    assert state.x == 10, "x should be 10"
    assert state.y == 20, "y should be 20"
    assert state.bearing == "north", "bearing should be 'north'"
    x, y, bearing = state
    assert x == 10 and y == 20 and bearing == "north", "Tuple unpacking failed"


def test_robot_wrap_around_east():
    """
    Verifies east-edge wrap-around movement.
    A robot moving east from the maximum x coordinate should reappear at x=0.
    """
    asteroid = Asteroid.from_dict({"x": 5, "y": 5})
    robot = Robot({"x": 5, "y": 2}, "east", asteroid)
    robot.move_forward()
    assert robot.x == 0 and robot.y == 2, f"Expected robot to wrap to (0,2), got ({robot.x},{robot.y})"


def test_robot_wrap_around_west():
    """
    Verifies west-edge wrap-around movement.
    A robot moving west from x=0 should reappear at the maximum x coordinate.
    """
    asteroid = Asteroid.from_dict({"x": 5, "y": 5})
    robot = Robot({"x": 0, "y": 3}, "west", asteroid)
    robot.move_forward()
    assert robot.x == 5 and robot.y == 3, f"Expected robot to wrap to (5,3), got ({robot.x},{robot.y})"


def test_robot_wrap_around_north():
    """
    Verifies north-edge wrap-around movement.
    A robot moving north from the maximum y coordinate should reappear at y=0.
    """
    asteroid = Asteroid.from_dict({"x": 5, "y": 5})
    robot = Robot({"x": 2, "y": 5}, "north", asteroid)
    robot.move_forward()
    assert robot.x == 2 and robot.y == 0, f"Expected robot to wrap to (2,0), got ({robot.x},{robot.y})"


def test_robot_wrap_around_south():
    """
    Verifies south-edge wrap-around movement.
    A robot moving south from y=0 should reappear at the maximum y coordinate.
    """
    asteroid = Asteroid.from_dict({"x": 5, "y": 5})
    robot = Robot({"x": 3, "y": 0}, "south", asteroid)
    robot.move_forward()
    assert robot.x == 3 and robot.y == 5, f"Expected robot to wrap to (3,5), got ({robot.x},{robot.y})"

