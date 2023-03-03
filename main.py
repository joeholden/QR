import numpy as np
import cv2
import pandas as pd
import math

"""
In Tag, Black (0) is 1 and White (255) is 0
Currently making version 2 QR Code
"""
PIXEL_PAD = 15
GRID_SIZE = 25
QUIET_ZONE = 4 * PIXEL_PAD
MODE = 'A'  # N: Numeric, A: Alphanumeric, B: Byte, K: Kanji
PATH_ALPHANUMERIC = "C:/Users/joema/Desktop/QR Code/alphanumeric encoding QR.xlsx"


def fill_square(image_array, tag_bit_grid_location):
    """
    Takes in a square array and fills the pixel in that array with 0 (black). Will work regardless of resolution
    :param image_array:2-dimensional array
    :param tag_bit_grid_location: reference to grid position in tag, regardless of image size
    """
    x, y = tag_bit_grid_location
    x *= PIXEL_PAD
    y *= PIXEL_PAD
    for i in range(x, x + PIXEL_PAD):
        for j in range(y, y + PIXEL_PAD):
            if i <= GRID_SIZE * PIXEL_PAD + PIXEL_PAD and j <= GRID_SIZE * PIXEL_PAD + PIXEL_PAD:
                image_array[j, i] = 0


def construct_finder_pattern():
    """
    Adds the finder pattern squares to an empty QR Tag array. These are the large squares in the three corners
    :return: an updated array with the pattern squares
    """
    white_image_array = np.full(((GRID_SIZE - 1) * PIXEL_PAD + PIXEL_PAD, (GRID_SIZE - 1) * PIXEL_PAD + PIXEL_PAD), 255)
    square_boundaries = [(0, 7, 0, 7), (0, 7, GRID_SIZE - 7, GRID_SIZE), (GRID_SIZE - 7, GRID_SIZE, 0, 7)]
    # (lower x, upper x, lower y, upper y) | [lower bound, upper bound not including)
    for bounds in square_boundaries:
        for i in range(bounds[0], bounds[1]):
            for j in range(bounds[2], bounds[3]):
                if (i == bounds[0]) or (i == bounds[1] - 1) or (i == bounds[1] and j != bounds[2]) or \
                        (j == bounds[2] and i != bounds[0]) or (j == bounds[3] - 1 and i != bounds[0]):
                    fill_square(white_image_array, (i, j))


    # Fill in Central Square Inside Bounding Box
    center_locations = [(3, 3), (3, GRID_SIZE - 4), (GRID_SIZE - 4, 3)]
    central_squares = []
    for (center_x, center_y) in center_locations:
        central_squares.append((center_x, center_y))
        central_squares.append((center_x - 1, center_y))
        central_squares.append((center_x + 1, center_y))
        central_squares.append((center_x, center_y - 1))
        central_squares.append((center_x - 1, center_y - 1))
        central_squares.append((center_x + 1, center_y - 1))
        central_squares.append((center_x, center_y + 1))
        central_squares.append((center_x - 1, center_y + 1))
        central_squares.append((center_x + 1, center_y + 1))
    for px in central_squares:
        fill_square(white_image_array, px)

    return white_image_array


def construct_alignment_pattern(image, center_location):
    """
    :param image:
    :param center_location: list containing center points of alignment squares. Single integer per position.
                            Indexed from 1 like the standard
                            Eg. Version 2 is [18], Version 7 is [22, 38]
    :return:
    """
    image_array = image
    for square in center_location:
        fill_square(image, (square - 1, square - 1))

        square_boundary = (square - 3, square + 2, square - 3, square + 2)
        # (lower x, upper x, lower y, upper y) | [lower bound, upper bound not including)
        for i in range(square_boundary[0], square_boundary[1]):
            for j in range(square_boundary[2], square_boundary[3]):
                if (i == square_boundary[0]) or (i == square_boundary[1] - 1) or (i == square_boundary[1] and j != square_boundary[2]) or \
                        (j == square_boundary[2] and i != square_boundary[0]) or (j == square_boundary[3] - 1 and i != square_boundary[0]):
                    fill_square(image_array, (i, j))

    return image_array


def add_timing_patterns(input_array):
    timing_patterned = input_array
    squares_to_blacken = []
    # vertical
    for i in range(8, GRID_SIZE-7):
        if i % 2 == 0:
            squares_to_blacken.append((6, i))
            squares_to_blacken.append((i, 6))
    for square in squares_to_blacken:
        fill_square(timing_patterned, square)
    return timing_patterned


# Build QR Tag
tag = construct_finder_pattern()
tag = add_timing_patterns(tag)
tag = construct_alignment_pattern(tag, [18])
tag = np.pad(tag, QUIET_ZONE, constant_values=255)

# Display and Save QR Tag
cv2.imshow('QR Tag', tag.astype(np.uint8))
cv2.waitKey()
cv2.destroyAllWindows()
cv2.imwrite('C:/Users/joema/Desktop/tes.png', tag)


def encode_data(data):
    data = data.upper()
    alphanumeric_table = pd.read_excel(PATH_ALPHANUMERIC, dtype=str)
    alphanumeric_dictionary = pd.Series(alphanumeric_table.Value.values, index=alphanumeric_table.Character).to_dict()

    character_values = []
    for character in data:
        character_values.append(alphanumeric_dictionary[character])

    character_groupings = []
    for index, value in enumerate(character_values):
        if index % 2 == 0:
            try:
                character_groupings.append((character_values[index], character_values[index + 1]))
            except IndexError:
                character_groupings.append((character_values[index], ))

    bits = []
    for group in character_groupings:
        try:
            v1 = int(group[0]) * 45
            v2 = int(group[1])
        except IndexError:
            value = int(group[0])
            bin_value = format(value, '#08b')
        else:
            value = v1 + v2
            bin_value = format(value, '#013b')
        bits.append(bin_value)

    binary_character_count_indicator = format(len(data), '#011b')
    mode_indicator = '0b0010'  #changes if this isn't alphanumeric

    bit_stream = mode_indicator[2:] + binary_character_count_indicator[2:]

    for b in bits:
        bit_stream = bit_stream + b[2:]
    print(bit_stream)


encode_data('Hello World')