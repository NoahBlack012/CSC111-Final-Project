"""CSC111 Final Project: Simplifying the UofT Course Selection Process

Description
===============================
This module includes helper functions.

Copyright and Usage Information
===============================
This file is Copyright (c) 2023 Noah Black, Nikita Goncharov and Adam Pralat.
"""


def split_string(string: str) -> str:
    """ A helper function that splits longer strings into multiple lines. """
    words = string.split()
    new_string = ''
    line_length = 0
    for word in words:
        if len(word) + line_length > 100:
            new_string += '\n'
            line_length = 0
        new_string += word + ' '
        line_length += len(word) + 1
    return new_string.strip()


if __name__ == '__main__':
    import python_ta
    import doctest

    doctest.testmod()
    python_ta.check_all(config={
        'extra-imports': ['json', 'course_network', 'requirements'],
        'allowed-io': ['get_course_tree'],
        'max-line-length': 120
    })
