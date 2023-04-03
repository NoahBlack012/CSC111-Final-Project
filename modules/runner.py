"""
Course Networks file

Copyright and Usage Information
===============================

This file is part of a Course Project for CSC111H1 of the University of
Toronto.

Copyright (c) 2023 Nikita Goncharov, Noah Black, Adam Pralat
"""


from __future__ import annotations

import json

import helper
from course_network import DatabaseCourseNetwork, PlannerCourseNetwork


def get_course_tree(c: str, taken: set[str]) -> PlannerCourseNetwork:
    """
    Get the course

    Preconditions:
    - c is a valid course code in the dataset
    - Every string in taken is a valid course code in the dataset
    """
    # Path to the JSON file
    json_file = "../data-processing/courses_clean.json"

    with open(json_file) as f:
        data = json.load(f)

        # Add all courses to course network
        course_network = DatabaseCourseNetwork(taken)
        for i in data:
            code = i['course code']
            course_network.add_course(code)

        # Add all course prereqs
        for i in data:
            reqs = helper.parse_course_requirements(i['prerequisites']).get_possible_true_combos()
            course = course_network.get_course(i['course code'])
            course.add_prereqs(reqs)

        course = course_network.get_course(c)

        # Get all possible prereq networks
        out = course_network.get_all_prereq_networks(course)

        # Get all prereq networks at the min length (Min duration to take all prereqs in network)
        min_lengths = [out[0]]
        min_length = out[0].length
        for i in out:
            if i.length == min_length:
                min_lengths.append(i)
            elif i.length < min_length:
                min_lengths = [i]
                min_length = i.length

        # Select the network of the networks at the min length to be the one with the fewest number of credits
        return min(min_lengths, key=lambda x: x.get_number_of_credits(taken))


if __name__ == '__main__':
    import python_ta
    import doctest

    doctest.testmod()
    python_ta.check_all(config={
        'extra-imports': ['json', 'course_network', 'helper'],
        'allowed-io': ['get_course_tree'],
        'max-line-length': 120
    })
