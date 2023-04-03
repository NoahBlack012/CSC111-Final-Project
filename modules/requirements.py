"""
CSC111 Final Project: Simplifying the UofT Course Selection Process

Description
===============================
File that contains code to process and model course requirements (i.e prerequisites)

Copyright and Usage Information
===============================

This file is part of a Course Project for CSC111H1 of the University of
Toronto.

Copyright (c) 2023 Nikita Goncharov, Noah Black, Adam Pralat
"""
from __future__ import annotations
from typing import Optional


class RequirementNode:
    """
    Class to represent a node in a course requirements

    _text: A string to represent the pure text in the node
    _sep: A string to represent the separator in the requirement
    _left: The left requirement node
    _right: The right requirement node

    Representation Invariants:
    - self._left is None == self._right is None
    - self._left is None == self._sep is None and self._right is None == self._sep is None
    """
    _text: str
    _sep: Optional[str]
    _left: Optional[RequirementNode]
    _right: Optional[RequirementNode]

    def __init__(self, text) -> None:
        self._text = text
        self._right = None
        self._left = None
        self._sep = None

    def get_truth_value(self, user_courses: set[str]) -> bool:
        if is_course_format(self._text) or self._text == '':
            # Base case - self._text is just a single courses
            # If the text is empty - There are no specific prereqs
            return self._text in user_courses or self._text == ''
        else:
            if self._sep == '^':
                # The separator is an and
                return self._left.get_truth_value(user_courses) and self._right.get_truth_value(user_courses)
            else:
                # The separator is an or
                return self._left.get_truth_value(user_courses) or self._right.get_truth_value(user_courses)

    def get_leaves_linked(self) -> set[str]:
        """
        Return all leaves linked to the node (Including itself possibly)
        """
        if self._text == '' or is_course_format(self._text):
            return {self._text}
        else:
            leaves_so_far = set()
            leaves_so_far = leaves_so_far.union(self._left.get_leaves_linked())
            leaves_so_far = leaves_so_far.union(self._right.get_leaves_linked())
            return leaves_so_far

    def get_possible_true_combos(self) -> list[set[str]]:
        """
        Return all possible course combinations that make the given node return a truth value of true

        >>> course = parse_course_requirements('CSC311H1|CSC411H1|STA314H1|ECE421H1|ROB313H1|CSCC11H3|CSC311H5')
        >>> all(course.get_truth_value(i) is True for i in course.get_possible_true_combos())
        True
        """
        if self._text == '':
            return [set()]
        elif is_course_format(self._text):
            return [{self._text}]
        else:
            if self._left is not None:
                left_rec = self._left.get_possible_true_combos()
            else:
                left_rec = []

            if self._right is not None:
                right_rec = self._right.get_possible_true_combos()
            else:
                right_rec = []
            if self._sep == '^':
                # If the separator is and, both left and right must return true for the
                # node to have a truth value of true

                combos_so_far = []

                for i in range(0, len(left_rec)):
                    for j in range(0, len(right_rec)):
                        if left_rec[i].union(right_rec[j]) not in combos_so_far:
                            combos_so_far.append(left_rec[i].union(right_rec[j]))
                return combos_so_far
            else:
                # If the separator is or, either the left or right nodes must return true for the
                # node to have a truth value of true
                return left_rec + right_rec

    def set_node_attributes(self, sep: str, left: RequirementNode, right: RequirementNode) -> None:
        """
        Set the attributes of the given node
        """
        self._sep = sep
        self._left = left
        self._right = right


def parse_course_requirements(requirements: str) -> RequirementNode:
    """
    Parse a course requirement string into a _Node (_Node will be the root of the tree)

    Preconditions:
    - requirements is a valid course requirements string

    >>> x = parse_course_requirements('')
    >>> x._text == ''
    True
    >>> x._sep is None
    True

    """
    # Make sure there is not a bracket at start and end of requirements string
    while is_enclosed_brackets(requirements):
        requirements = requirements[1:-1]

    if is_course_format(requirements) or requirements == '':
        # Base case - Requirements is just a single course or is an empty string
        return RequirementNode(requirements)
    else:
        curr_node = RequirementNode(requirements)

        # Group courses by brackets with separators between brackets included in list
        # If a bracket/separator is encountered, reset curr_item?? If in brackets, ignore separators
        bracket_level = 0
        curr_group = ''
        course_groups = []
        for i in requirements:
            if i == '(':
                bracket_level += 1
            elif i == ')':
                bracket_level -= 1

            if bracket_level == 0 and i in ('|', '^'):
                course_groups.append(curr_group)
                curr_group = ''
                course_groups.append(i)
            elif bracket_level > 0 and i in ('|', '^'):
                curr_group += i
            elif i not in ('|', '^'):
                curr_group += i
        if curr_group != '':
            course_groups.append(curr_group)

        if '^' in course_groups:
            # If ^ in grouped list - Search for first ^ in grouped list
            i = 0
            first_group = ''
            sep = '^'
            while course_groups[i] != '^':
                first_group += course_groups[i]
                i += 1
            second_group = ''.join(course_groups[i + 1:])
        else:
            # Otherwise, search for first | in grouped list
            i = 0
            first_group = ''
            sep = '|'
            while course_groups[i] != '|':
                first_group += course_groups[i]
                i += 1
            second_group = ''.join(course_groups[i + 1:])

        # Store separator + Courses before and after seperator
        curr_node.set_node_attributes(
            sep,
            parse_course_requirements(first_group),
            parse_course_requirements(second_group)
        )
        return curr_node

def is_enclosed_brackets(s: str) -> bool:
    """
    Return whether a string is fully enclosed by one pair of brackets

    >>> is_enclosed_brackets('()')
    True
    >>> is_enclosed_brackets('(((ABCDE)))')
    True
    >>> is_enclosed_brackets('(ABC)^(DEF)')
    False
    >>> is_enclosed_brackets('()ABCDE')
    False
    """
    if s == '' or s[0] != '(':
        return False
    else:
        open_bracket = 1
        for i in s[1:]:
            if open_bracket == 0:
                return False
            if i == '(':
                open_bracket += 1
            elif i == ')':
                open_bracket -= 1
        return True


def is_course_format(s: str) -> bool:
    """
    Helper function - Return whether a string is in the format of a course

    >>> is_course_format("CSC111H1")
    True
    >>> is_course_format("CSCAA1")
    False
    >>> is_course_format("")
    False
    """
    return len(s) == 8 and s[0:3].isalpha() and (s[3:6].isnumeric() or (s[4:6].isnumeric())) and s[6].isalpha() and \
            s[7].isnumeric()

if __name__ == '__main__':
    import python_ta
    import doctest
    doctest.testmod()
    python_ta.check_all(config={
        'extra-imports': [],
        'allowed-io': [''],
        'max-line-length': 120
    })
