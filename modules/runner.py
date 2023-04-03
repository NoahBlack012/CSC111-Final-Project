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
import itertools

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

def run_multiple(courses: set[str], taken: set[str]) -> list[PlannerCourseNetwork]:
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

        all_planers = []
        for c in courses:
            course = course_network.get_course(c)
            possible_planners = course_network.recur2(course) #TODO: Rename recur2
            all_planers.append(possible_planners)
        print (len(all_planers[1]))

        return select_planner_network_multiple(all_planers, taken)

def select_planner_network_multiple(planners: list[list[PlannerCourseNetwork]], taken: set[str]) -> list[PlannerCourseNetwork]:
    """
    Select the optimal set of planner networks to reach multiple courses
    """
    # Generate all possible combos of planners
    all_planner_combos = [list(i) for i in itertools.product(*planners)]
    print (len(all_planner_combos))
    min_length_planner_combos = [all_planner_combos[0]]
    # Length of planner combo is max length of individual planners
    min_length_planner = max(all_planner_combos[0], key=lambda x:x.length).length
    for combo in all_planner_combos:
        combo_length = max(combo, key=lambda x: x.length).length
        if combo_length == min_length_planner:
            min_length_planner_combos.append(combo)
        elif combo_length < min_length_planner:
            min_length_planner_combos = [combo]
            min_length_planner = combo_length

    # Tiebreak based on which combo takes a fewer number of credits
    return min(min_length_planner_combos, key=lambda x: get_planner_combo_credits(x, taken))

def get_planner_combo_credits(planner_combo: list[PlannerCourseNetwork], visited: set[str]) -> int:
    """
    Return the number of credits required to complete the given combo of networks
    """
    # Note Y courses are counted as 2 credits and H courses are counted as 1 credit so the credits for a network
    # can be stored as an int
    credits_so_far = 0
    for planner in planner_combo:
        for course in planner.courses:
            if isinstance(course, set):
                for c in course:
                    # Only add the credit for the course if the course has not been counted already
                    if c.data.code not in visited:
                        credits_so_far += c.data.duration
                        visited = visited.union({c.data.code})
            else:
                # Only add the credit for the course if the course has not been counted already
                if course.data.code not in visited:
                    credits_so_far += course.data.duration
                    visited = visited.union({course.data.code})

    return credits_so_far

if __name__ == '__main__':
    c = ['CSC311H1', 'CSC443H1']
    taken = set()

    out = run_multiple(c, taken)
    for i in out:
        print (str(i))
