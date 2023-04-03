"""
CSC111 Final Project: Simplifying the UofT Course Selection Process

Description
===============================
A file to cleaned data scraped from the UofT course search website
Note that this file is never run during the running of the main file of the program, it was already run to build the
dataset that the program runs.

Copyright and Usage Information
===============================
This file is Copyright (c) 2023 Noah Black, Nikita Goncharov and Adam Pralat.
"""

import json


def clean_data(input_file: str, output_file: str) -> None:
    """
    Clean the course data stored in the input file (A json file) and output the cleaned data in the output file (Another
    json file)

    Preconditions:
    - input_file is a valid path to a json file in
    """
    with open(input_file, 'r') as f:
        file = json.load(f)

    out = []
    for line in file:
        # Clean all course requirements
        line["prerequisites"] = clean_course_requirements(line["prerequisites"])
        line["corequisites"] = clean_course_requirements(line["corequisites"])
        line["exclusions"] = clean_course_requirements(line["exclusions"])
        out.append(line)

    with open(output_file, 'w') as f:
        json.dump(out, f, indent=4)


def clean_course_requirements(requirements: str) -> str:
    """
    Clean a course requirment string

    The following components are cleaned:
    1) Remove double separators (Ex: ^^ or ||)
    2) Remove separators in certain positions relative to brackets (For example, |) carries no logical meaning)
    3) Cut the string so it does not begin or end with separators (Separators at these locations carry no logical
    meaning

    >>> clean_course_requirements('||^|')
    ''
    >>> clean_course_requirements('ARH482H1(^)^^')
    'ARH482H1'
    """
    # Replace double separators with single separators
    while '^^' in requirements or '||' in requirements:
        requirements = requirements.replace('^^', '^')
        requirements = requirements.replace('||', '|')

    # Remove separators beside parantheses that carry no logical meaning
    # Ex: (^, (|, ^), |)
    while '(^' in requirements or '(|' in requirements or '^)' in requirements or '|)' in requirements:
        requirements = requirements.replace('(^', '(')
        requirements = requirements.replace('(|', '(')
        requirements = requirements.replace('^)', ')')
        requirements = requirements.replace('|)', ')')

    # Remove empty brackets from requirements
    requirements = requirements.replace('()', '')

    # Remove separators from start and end of requirements string
    i = 0
    while i < len(requirements) and requirements[i] in (')', '^', '|'):
        i += 1
    start = i

    i = len(requirements) - 1
    while i >= 0 and requirements[i] in ('(', '^', '|'):
        i -= 1
    end = i + 1

    # Return an empty string if either start or end are not valid indicies
    if start >= len(requirements) or end < 0:
        return ''
    else:
        requirements = requirements[start:end]

    return requirements


if __name__ == '__main__':
    import python_ta
    import doctest

    doctest.testmod()
    python_ta.check_all(config={
        'extra-imports': ['json'],
        'allowed-io': ['clean_data'],
        'max-line-length': 120
    })
