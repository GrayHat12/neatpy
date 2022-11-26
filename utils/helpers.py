def normalize(x: list, newRange=(0, 1)):  # x is an array. Default range is between zero and one
    xmin, xmax = min(x), max(x)  # get max and min from input array
    norm = (x - xmin)/(xmax - xmin)  # scale between zero and one

    if newRange == (0, 1):
        return (norm)  # wanted range is the same as norm
    elif newRange != (0, 1):
        # scale to a different range.
        return norm * (newRange[1] - newRange[0]) + newRange[0]
    raise ValueError("Invalid range")


def normalize_value(value: float, min_value: float, max_value: float, range=(0, 1)) -> float:
    if max_value == min_value:
        max_value = min_value + 1
    norm = (value - min_value) / (max_value - min_value)
    return norm * (range[1] - range[0]) + range[0]