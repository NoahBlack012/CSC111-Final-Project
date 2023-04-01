"""
TOOD: Add file docstring
"""

from __future__ import annotations
from typing import Optional

from treelib import Tree


class DatabaseCourse:
    """
    TODO: Add docstring

    """

    code: str
    credit_value: float
    duration: int
    # corequisites: BoolOp | None
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
    Graph to represent all courses
    TODO: Add docstring

    """

    courses: list[DatabaseCourse]

    def __init__(self):
        self.courses = []

    def add_course(self, code: str) -> DatabaseCourse:
        """
        TODO
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

        self.courses.append(new_course)

        return new_course

    def get_course(self, code: str) -> DatabaseCourse | None:
        """TODO"""
        for course in self.courses:
            if course.code == code:
                return course

        return None

    def recur(self, start: DatabaseCourse) -> PlannerCourseNetwork:
        """
        recursive traversal of courses and prereqs
        """

        if start.prerequisites == [set()]:
            return PlannerCourseNetwork(start)

        possible_prereqs = start.prerequisites

        # first one to get maximum
        prereq_networks_to_merge = []
        for req in possible_prereqs[0]:
            course = self.get_course(req)
            if course is not None:
                prereq_networks_to_merge.append(self.recur(course))
            # elif req[-1] == '1':
            #     raise Exception('unknown prerequisite \'' + req + '\' for course \'' + start.code + '\'')

        shortest_merged_network = PlannerCourseNetwork()
        shortest_merged_network.merge_networks(prereq_networks_to_merge, start)

        for reqs in possible_prereqs:
            prereq_networks_to_merge = []
            invalid_course = False
            for req in reqs:
                course = self.get_course(req)
                if course is not None:
                    prereq_networks_to_merge.append(self.recur(course))
                # elif req[-1] == '1':
                #     raise Exception('unknown prerequisite \'' + req + '\' for course \'' + start.code + '\'')
                else:
                    invalid_course = True

            if invalid_course:
                break

            merged_network = PlannerCourseNetwork()
            merged_network.merge_networks(prereq_networks_to_merge, start)

            if shortest_merged_network.length > merged_network.length:
                shortest_merged_network = merged_network

        return shortest_merged_network

        # if start.prerequisites is None or start.corequisites is None:
        #     return PlannerCourseNetwork(start)
        #
        # prereq_evaluated = start.prerequisites.evaluate(self)
        # prereq_networks_to_merge = []
        #
        # for prereq in prereq_evaluated:
        #     prereq_networks_to_merge.append(self.recur(prereq))
        #
        # # coreq_networks_to_merge = []
        #
        # combined = PlannerCourseNetwork()
        #
        # combined.merge_networks(prereq_networks_to_merge, start)
        #
        # combined.length = combined.length + start.duration
        # return combined


class PlannerSlot:
    """
    TODO
    """
    data: DatabaseCourse | set[DatabaseCourse]
    next_course: Optional[PlannerSlot]

    def __init__(self, data: DatabaseCourse | set[DatabaseCourse]):
        self.data = data
        self.next_course = None


class PlannerCourseNetwork:
    """
    TODO
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

    def merge_networks(self, networks: list[PlannerCourseNetwork], end: DatabaseCourse | set[DatabaseCourse]) -> None:
        """
        TODO
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

        # for network in networks:
        #     network.end = slot

        self.end = slot

        self.length = max([network.length for network in networks]) + end.duration

    def __str__(self):
        """TODO"""

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
        """TODO"""

        s = [prereq[1] for prereq in helper_dict if prereq[0] == root]

        for prereq in s:
            if not tree.contains(prereq):
                tree.create_node(prereq, prereq, parent=root)

        for prereq in s:
            self._str_recur_helper(tree, helper_dict, prereq)

        return tree
