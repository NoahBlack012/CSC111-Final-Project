"""
CSC111 Final Project: Simplifying the UofT Course Selection Process

Description
===============================
Course Networks file

Copyright and Usage Information
===============================

This file is part of a Course Project for CSC111H1 of the University of
Toronto.

Copyright (c) 2023 Nikita Goncharov, Noah Black, Adam Pralat
"""

from __future__ import annotations
from typing import Optional

import itertools
from treelib import Tree


class DatabaseCourse:
    """
    A course node object for the database network.

    Instance Attriutes:
        - code: course code
        - credit_value: the credit value of the course
        - duration: the duration of the course in terms
        - prerequisites: the list of all possible course combinations that fulfill the course's prerequisites

    Representation Invariants:
    - code is a valid course code in the dataset

    """
    code: str
    credit_value: float
    duration: int
    prerequisites: list[set[str]]

    def __init__(self, code: str, credit_value: float, duration: int) -> None:
        self.code = code
        self.credit_value = credit_value
        self.duration = duration

    def add_prereqs(self, prereqs: list[set[str]]) -> None:
        """Set the courses prereqs"""
        self.prerequisites = prereqs


class DatabaseCourseNetwork:
    """
    Graph to represent the database of all courses

    Instance Attributes:
        - courses: a dictionary mapping course codes into DatabaseCourse objects
        - courses_taken: the set of course that the user has already taken

    Representation Invariants:
    - courses_taken cotains a set of valid course code in the dataset

    """
    courses: dict[str, DatabaseCourse]
    courses_taken: set[str]

    def __init__(self, courses_taken: set[str]) -> None:
        self.courses = {}
        self.courses_taken = courses_taken

    def add_course(self, code: str) -> DatabaseCourse:
        """
        Add a course to the network, and return it.
        Raise a ValueError if the second last character is not an H or a Y

        """
        if code[-2] == 'H':
            duration = 1
            credit = 0.5
        elif code[-2] == 'Y':
            duration = 2
            credit = 1.0
        else:
            duration = 0
            credit = 0.0
            raise ValueError

        new_course = DatabaseCourse(code, credit, duration)

        self.courses[code] = new_course

        return new_course

    def get_course(self, code: str) -> DatabaseCourse | None:
        """
        Get the DatabaseCourse for the corresponiding course code.

        If courses doesn't exit, return None
        """

        if code in self.courses:
            return self.courses[code]
        return None

    def get_all_prereq_networks(self, start: DatabaseCourse) -> list[PlannerCourseNetwork]:
        """
        Get a list of every possible set of prereqs for the given courses, outputed as a list of PlannerCourseNetworks

        Preconditions:
        - start is a valid course in the DatabaseCourseNetwork
        """
        # If the current course has no prerequisites, the only planner network is the one with just the current
        # course
        if start.prerequisites == [set()]:
            return [PlannerCourseNetwork(start)]

        # Get the list of possible prerequisites
        possible_prereqs = start.prerequisites

        networks = []

        for req in possible_prereqs:
            # If the user already has the given set of prereqs, one planner network is the one with just the current
            # course
            if req.issubset(self.courses_taken):
                networks.append(PlannerCourseNetwork(start))
        for reqs in possible_prereqs:
            # Get a list of lists of all possible planner networks for the current prereqs courses
            current_req_planner_networks = []
            invalid_course = False
            for req in reqs:
                if req in self.courses_taken:
                    continue

                # If a course in the current set of prereqs is not in the network, that entire set of prereqs is invalid
                course = self.get_course(req)
                if course is not None:
                    # Recursively get every possible planner network for the given course
                    possible_req_planner_networks = self.get_all_prereq_networks(course)
                    current_req_planner_networks.append(possible_req_planner_networks)
                else:
                    invalid_course = True

            if invalid_course:
                continue

            # Get every possible combo of courses to fufill the current prereq set
            possible_network_combos = [list(i) for i in itertools.product(*current_req_planner_networks)]
            for prereq_network_combo in possible_network_combos:
                if prereq_network_combo != []:
                    # Get the full network for the current combo of prereqs
                    merged_network = PlannerCourseNetwork()
                    merged_network.merge_networks(list(prereq_network_combo), start)
                    networks.append(merged_network)

        # Return all possible prereq networks
        return networks


class PlannerSlot:
    """
    A slot node object for the PlannerCourseNetwork

    Instace Attributes:
        - data: the DatabaseCourse that is stored in the slot
        - next_course: the next course to take according to planner
    """
    data: DatabaseCourse
    next_course: Optional[PlannerSlot]

    def __init__(self, data: DatabaseCourse) -> None:
        self.data = data
        self.next_course = None


class PlannerCourseNetwork:
    """
    Tree-like network to represnt the sequence of courses to take

    Instance Attributes:
        - starts: list of starting slots in the planner
        - courses: list of all slots in the planner
        - end: the last course in the planner (root)
        - length: the duration of the longest sequence of courses in the planner, in terms
    """
    starts: list[PlannerSlot]
    courses: list[PlannerSlot]
    end: PlannerSlot
    length: int

    def __init__(self, course: [DatabaseCourse | None] = None) -> None:
        if course is not None:
            slot = PlannerSlot(course)
            self.courses = [slot]
            self.starts = [slot]
            self.end = slot
            if not isinstance(course, set):
                self.length = course.duration
            else:
                self.length = 1
        else:
            self.starts = []
            self.courses = []
            self.length = 0

    def merge_networks(self, networks: list[PlannerCourseNetwork], end: DatabaseCourse) -> None:
        """
        Merge a list of PlannerCourseNetworks to all end at a slot containing the given DatabaseCourse
        """
        for network in networks:
            for start in network.starts:
                self.starts.append(start)
            for course in network.courses:
                self.courses.append(course)

        slot = PlannerSlot(end)
        self.courses.append(slot)

        for network in networks:
            network.end.next_course = slot

        self.end = slot
        self.length = max([n.length for n in networks]) + end.duration

    def __str__(self) -> str:
        """
        Return the string representation of the PlannerCourseNetwork
        """

        helper_dict = []
        root = ''

        for course in self.courses:
            if course.next_course is not None:
                key = course.next_course.data.code
                val = course.data.code
                helper_dict.append((key, val))
            else:
                root = course.data.code

        tree = Tree()
        tree.create_node(root, root)

        self._str_recur_helper(tree, helper_dict, root)

        ret = str(tree)
        return ret

    def _str_recur_helper(self, tree: Tree, helper_dict: list, root: str) -> Tree:
        """
        recursive helper function for __str__
        """

        s = [p[1] for p in helper_dict if p[0] == root]

        for prereq in s:
            if not tree.contains(prereq):
                tree.create_node(prereq, prereq, parent=root)

        for prereq in s:
            self._str_recur_helper(tree, helper_dict, prereq)

        return tree

    def get_number_of_credits(self, visited: set[str]) -> int:
        """
        Return the number of credits required to complete the given network
        """
        # Note Y courses are counted as 2 credits and H courses are counted as 1 credit so the credits for a network
        # can be stored as an int
        credits_so_far = 0

        for course in self.courses:
            if isinstance(course, set):
                for c in course:
                    if c.data.code not in visited:
                        credits_so_far += c.data.duration
                        visited = visited.union({c.data.code})
            else:
                if course.data.code not in visited:
                    credits_so_far += course.data.duration
                    visited = visited.union({course.data.code})
        return credits_so_far


if __name__ == '__main__':
    import python_ta
    import doctest
    doctest.testmod()
    python_ta.check_all(config={
        'extra-imports': ['treelib', 'itertools'],
        'allowed-io': [''],
        'max-line-length': 120
    })
