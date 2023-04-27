import logging
from dataclasses import dataclass
from collections import abc

import numpy as np

# quick and dirty solution for keeping these values
min_x = 0.0
min_y = 0.0

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@dataclass
class Coordinate:
    x: float
    y: float
    angle: float


def main() -> None:
    dim, n_points, coordinates = parse_input()

    convex_hull = _find_convex_hull(n_points, coordinates)

    _display_output(convex_hull)


def parse_input() -> tuple[int, int, list[Coordinate]]:
    logging.warning('#'*50)
    dim, n_points = [int(entry) for entry in input().split(' ')]

    coordinates: list[Coordinate] = []
    for _ in range(n_points):
        x, y = [float(coordinate) for coordinate in input().split('#')[1].strip().split(' ')]
        coordinate = Coordinate(x, y, ...)  # angle to be filled in
        coordinates.append(coordinate)

    return dim, n_points, coordinates


def _find_convex_hull(n_points: int, coordinates: abc.Sequence[Coordinate]) -> list[Coordinate]:
    """Find convex hull using Graham scan."""
    coordinates = _update_origo(coordinates)
    coordinates = sorted(coordinates, key=lambda coord: coord.angle)

    start_index = 3

    # list efficiently implements a stack
    convex_hull: list[Coordinate] = []
    convex_hull.extend(coordinates[:start_index])

    # if first three are collinear, remove the one closest to root
    while _is_collinear(convex_hull[-3], convex_hull[-2], convex_hull[-1]):
    #if convex_hull[-1].angle == convex_hull[-2].angle:
        if _distance_to(convex_hull[-1]) > _distance_to(convex_hull[-2]):
            res = convex_hull.pop(-2)
            _warn(res, 'popped early because collinear')
        else:
            res = convex_hull.pop()
            _warn(res, 'popped early because collinear')
        # push next node to stack
        convex_hull.append(coordinates[start_index])
        # postpone start
        start_index += 1

    # if right turn, let next_point point to the point which made us turn right
    # do this until we find no more right turns: this node is part of the convex hull
    for index, coordinate_test in enumerate(coordinates[start_index:]):
        _warn(coordinate_test, f'Stack: {len(convex_hull)=}')
        # use this test coordinate to see if the node on top of stack is in our outside CH
        # has to be while loop since we have to re-test the top-of-stack node for right turns using all remaining nodes
        while _is_right_turn(convex_hull[-2], convex_hull[-1], coordinate_test):
            # logging.warning(f' {index} | Popping top of stack {convex_hull}')
            # top is not in CH!
            _warn(coordinate_test, 'Popping')
            convex_hull.pop()

        _warn(coordinate_test, 'Pushing...')
        convex_hull.append(coordinate_test)

        # if the last node is collinear with root and the next to last, remove it
        if index == (len(coordinates) - 3) - 1:
            if _is_collinear(convex_hull[-2], convex_hull[-1], convex_hull[0]):
                _warn(convex_hull[-1], 'Removing last due to collinearity')
                convex_hull.pop()

    return convex_hull


def _update_origo(coordinates: abc.Sequence[Coordinate]) -> list[Coordinate]:
    coordinate_min_y = min(coordinates, key=lambda coord: coord.y)

    # quick and dirty solution for keeping these values
    global min_y, min_x
    min_y = coordinate_min_y.y
    min_x = coordinate_min_y.x

    #logging.warning(f'{min_x=}; {min_y} ')
    for coordinate in coordinates:
        coordinate.y -= min_y
        coordinate.x -= min_x
        coordinate.angle = _calculate_angle(coordinate)

    return coordinates


def _calculate_angle(coordinate: Coordinate) -> float:
    # arctan only gives correct angle for positive x
    angle_offset = np.pi if coordinate.x < 0 else 0
    angle = (
        np.arctan(coordinate.y / coordinate.x)
        if coordinate.x
        # straight up or down in R^2
        else np.pi / 2 * np.sign(coordinate.y)
    )
    return angle + angle_offset


def _distance_to(coordinate: Coordinate):
    """Calculate squared distance to coordinate from root."""
    return coordinate.x**2 + coordinate.y**2


def _warn(coordinate: Coordinate, msg: str) -> None:
    logging.warning(f' {coordinate.x + min_x}, {coordinate.y + min_y} | {msg}')


def _is_right_turn(
    next_top: Coordinate,
    top: Coordinate,
    coordinate_test: Coordinate
) -> bool:
    vector_to_top_of_stack = _to_vector(next_top, top)  # [top.x - next_top.x, top.y - next_top.y]
    vector_to_next_coord = _to_vector(top, coordinate_test)  # [coordinate_test.x - top.x, coordinate_test.y - top.y]

    logging.warning(f' {top.x}, {top.y} | _is_right_turn: {np.cross(vector_to_top_of_stack, vector_to_next_coord)} <= 0')
    return np.cross(vector_to_top_of_stack, vector_to_next_coord) <= 0


def _is_collinear(coord_1, coord_2, coord_3):
    vector_1 = _to_vector(coord_1, coord_2)
    vector_2 = _to_vector(coord_2, coord_3)

    return np.cross(vector_1, vector_2) == 0


def _to_vector(coord_1, coord_2):
    """Compute vector pointing from coord_1 to coord_2"""
    return [coord_2.x - coord_1.x, coord_2.y - coord_1.y]


def _display_output(convex_hull: list[Coordinate]) -> None:
    # reorder according to PH
    convex_hull = _reorder_list_ph_format(convex_hull)

    print(len(convex_hull))
    # TODO: make sure these are in the desired orded according to PH algo
    for coordinate in convex_hull:
        # cast to int if possible
        # if coordinate.x == int(coordinate.x) and coordinate.y == int(coordinate.y):
        #    x, y = int(coordinate.x), int(coordinate.y)
        #    _min_x, _min_y = int(min_x), int(min_y)
        # else:
        x, y = coordinate.x, coordinate.y
        _min_x, _min_y = min_x, min_y

        original_x = x + _min_x
        original_y = y + _min_y

        # convert to int only if very close to integer
        if np.isclose(original_x, int(original_x), atol=1e-3):
            original_x, original_y = int(original_x), int(original_y)
            print(original_x, original_y)
        else:
            print(f'{round(original_x, 3):.3f} {round(original_y, 3):.3f}')


def _reorder_list_ph_format(convex_hull: list[Coordinate]) -> list[Coordinate]:
    # first node is rightmost node, then in the clockwise direction
    convex_hull_clock_order = list(reversed(convex_hull))

    rightmost_node = max(convex_hull_clock_order, key=lambda coordinate: coordinate.x)
    index_rightmost_node = convex_hull_clock_order.index(rightmost_node)

    convex_hull_reordered = convex_hull_clock_order[index_rightmost_node:] + convex_hull_clock_order[:index_rightmost_node]

    return convex_hull_reordered


if __name__ == '__main__':
    main()