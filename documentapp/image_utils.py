def denormalise_box_coordinates(
    start_x_norm: float,
    start_y_norm: float,
    end_x_norm: float,
    end_y_norm: float,
    doc_width: float,
    doc_height: float,
) -> tuple[int, int, int, int]:
    start_x = int(start_x_norm * doc_width)
    end_x = int(end_x_norm * doc_width)
    start_y = int(start_y_norm * doc_height)
    end_y = int(end_y_norm * doc_height)

    return start_x, start_y, end_x, end_y


def get_box_coords(start_x: int, start_y: int, end_x: int, end_y: int) -> list[list[int]]:
    return [[start_x, start_y], [end_x, start_y], [end_x, end_y], [start_x, end_y]]
