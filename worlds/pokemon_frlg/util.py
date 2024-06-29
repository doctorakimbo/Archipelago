from typing import List


HM_TO_COMPATABILITY_ID = {
    "Cut": 50,
    "Fly": 51,
    "Surf": 52,
    "Strength": 53,
    "Flash": 54,
    "Rock Smash": 55,
    "Waterfall": 56
}


def int_to_bool_array(num: int) -> List[bool]:
    binary_string = format(num, "064b")
    bool_array = [bit == "1" for bit in reversed(binary_string)]
    return bool_array
