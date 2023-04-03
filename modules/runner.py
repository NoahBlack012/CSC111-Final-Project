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

from helper import *
from course_network import DatabaseCourseNetwork, PlannerCourseNetwork


def run(c: str, taken: set[str]) -> PlannerCourseNetwork:
    """
    Runner file that returns a PlannerCourseNetwork for the given course code and set of taken courses' codes
    """
    json_file = "../data-processing/courses_clean.json"

    with open(json_file) as f:

        data = json.load(f)

        course_network = DatabaseCourseNetwork(taken)
        for i in data:
            code = i['course code']
            course_network.add_course(code)

        for i in data:
            reqs = parse_course_requirements(i['prerequisites']).get_possible_true_combos()
            course = course_network.get_course(i['course code'])
            course.add_prereqs(reqs)

        course = course_network.get_course(c)

        planner = course_network.recur(course)

        return planner


if __name__ == '__main__':
    c = 'MGY378H1'
    taken = set()
    planner = run(c, taken)
    print(f"Length: {planner.length}")
    print(str(planner))
    print("-------------------------------")
    print()
    json_file = "../data-processing/courses_clean.json"

    with open(json_file) as f:

        data = json.load(f)

        course_network = DatabaseCourseNetwork(taken)
        for i in data:
            code = i['course code']
            course_network.add_course(code)

        for i in data:
            reqs = parse_course_requirements(i['prerequisites']).get_possible_true_combos()
            course = course_network.get_course(i['course code'])
            course.add_prereqs(reqs)

        course = course_network.get_course(c)

    out = course_network.recur2(course)
    min_lengths = [out[0]]
    min_length = out[0].length
    for i in out:
        if i.length == min_length:
            min_lengths.append(i)
        elif i.length < min_length:
            min_lengths = [i]
            min_length = i.length

    optimal_tree = min(min_lengths, key=lambda x: x.get_duration(taken))
    print (str(optimal_tree))
