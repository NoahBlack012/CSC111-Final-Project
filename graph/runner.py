"""
temp Runner file TODO
"""

from __future__ import annotations

import json

from helper import *
from course_network import DatabaseCourseNetwork, PlannerCourseNetwork


def run(c: str) -> PlannerCourseNetwork:
    """
    TODO
    """
    json_file = "../data-procesing/courses_clean.json"

    with open(json_file) as f:

        data = json.load(f)

        course_network = DatabaseCourseNetwork()
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
    planner = run('CSC443H1')
    print(str(planner))
