"""
Course Networks file

Copyright and Usage Information
===============================

This file is part of a Course Project for CSC111H1 of the University of
Toronto.

Copyright (c) 2023 Nikita Goncharov, Noah Black, Adam Pralat
"""

from __future__ import annotations
from typing import Optional

from treelib import Tree


class DatabaseCourse:
    """
    A course node object for the database network.

    Instance Attriutes:
        - code: course code
        - credit_value: the credit value of the course
        - duration: the duration of the course in terms
        - prerequisites: the list of all possible course combinations that fulfill the course's prerequisites

    """

    code: str
    credit_value: float
    duration: int
    prerequisites: list[set[str]]

    def __init__(self, code: str, credit_value: float, duration: int):
        self.code = code
        self.credit_value = credit_value
        self.duration = duration

    def add_prereqs(self, prereqs: list[set[str]]):
        """TODO"""
        self.prerequisites = prereqs


class DatabaseCourseNetwork:
    """
    Graph to represent the database of all courses

    Instance Attributes:
        - courses: a dictionary mapping course codes into DatabaseCourse objects
        - courses_taken: the set of course that the user has already taken

    """

    courses: dict[str, DatabaseCourse]
    courses_taken: set[str]

    def __init__(self, courses_taken: set[str]):
        self.courses = dict()
        self.courses_taken = courses_taken

    def add_course(self, code: str) -> DatabaseCourse:
        """
        Add a course to the network, and return it.

        Preconditions:

        """
        if code[-2] == 'H':
            duration = 1
            credit = 0.5
        elif code[-2] == 'Y':
            duration = 2
            credit = 1.0
        else:
            raise Exception()

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

    def recur(self, start: DatabaseCourse) -> PlannerCourseNetwork:
        """
        Recursive function that returns a PlannerCourseNetwork for a given DatabaseCourse
        """

        if start.prerequisites == [set()]:
            return PlannerCourseNetwork(start)

        possible_prereqs = start.prerequisites

        for req in possible_prereqs:
            if req.issubset(self.courses_taken):
                return PlannerCourseNetwork(start)

        # first one to get maximum
        prereq_networks_to_merge = []
        for req in possible_prereqs[0]:
            if req in self.courses_taken:
                continue
            course = self.get_course(req)
            if course is not None:
                prereq_networks_to_merge.append(self.recur(course))

        shortest_merged_network = PlannerCourseNetwork()
        shortest_merged_network.merge_networks(prereq_networks_to_merge, start)

        for reqs in possible_prereqs:
            prereq_networks_to_merge = []
            invalid_course = False
            for req in reqs:
                if req in self.courses_taken:
                    continue
                course = self.get_course(req)
                if course is not None:
                    prereq_networks_to_merge.append(self.recur(course))
                else:
                    invalid_course = True

            if invalid_course:
                continue

            merged_network = PlannerCourseNetwork()
            merged_network.merge_networks(prereq_networks_to_merge, start)

            if shortest_merged_network.length > merged_network.length:
                shortest_merged_network = merged_network

        return shortest_merged_network


class PlannerSlot:
    """
    A slot node object for the PlannerCourseNetwork

    Instace Attributes:
        - data: the DatabaseCourse that is stored in the slot
        - next_course: the next course to take according to planner
    """
    data: DatabaseCourse
    next_course: Optional[PlannerSlot]

    def __init__(self, data: DatabaseCourse):
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

    def __init__(self, course=None):
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

        self.length = max([network.length for network in networks]) + end.duration

    def __str__(self):
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

        s = [prereq[1] for prereq in helper_dict if prereq[0] == root]

        for prereq in s:
            if not tree.contains(prereq):
                tree.create_node(prereq, prereq, parent=root)

        for prereq in s:
            self._str_recur_helper(tree, helper_dict, prereq)

        return tree
