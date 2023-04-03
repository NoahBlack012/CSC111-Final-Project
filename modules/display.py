"""CSC111 Final Project: Simplifying the UofT Course Selection Process

Description
===============================
Uses tkinter to create an interactive window.

Copyright and Usage Information
===============================
This file is Copyright (c) 2023 Noah Black, Nikita Goncharov and Adam Pralat.
"""
import tkinter as tk
import json
import doctest
import python_ta
from runner import get_course_tree
from helpers import split_string


def run_program() -> None:
    """ Creates a tkinter window which the user can interact with."""

    # load course data
    with open('../data-processing/courses_clean.json') as file:
        file_contents = json.load(file)

    # create the tkinter window
    root = tk.Tk()
    root.title("Simplifying the Course Selection Process")

    # Introduction
    tk.Label(root, text="Welcome to the UofT Course Selection Simplifier!\
    \nThis program takes in the course that a student wants to complete, as well as the courses the student has\
 already completed (if none, leave the boxes empty),\nand recommends the shortest sequence of courses for the student\
 so that they can complete all required prerequisites and corequisites for their desired course.\
    \nPlease refer to the project report for more details.\n").grid(row=0, column=0, columnspan=4)

    # Frame 1: For Completed Courses
    frame1 = tk.LabelFrame(root, text="What courses have you completed?", padx=15, pady=15)
    frame1.grid(row=1, column=0)

    # create labels and entry boxes for the user to input completed courses
    completed_labels = {0: tk.Label(frame1, text="Course Code:")}
    completed_entries = {0: tk.Entry(frame1)}
    completed_labels[0].grid(row=0, column=0)
    completed_entries[0].grid(row=0, column=1)

    # create a button to add more courses
    def add_completed_course_box() -> None:
        """ Creates a new label and entry box, and shifts everything else down."""
        index = len(completed_labels)
        # creates new label
        completed_labels[index] = tk.Label(frame1, text="Course Code:")
        completed_labels[index].grid(row=index + 1, column=0)
        # creates new entry box
        completed_entries[index] = tk.Entry(frame1)
        completed_entries[index].grid(row=index + 1, column=1)
        # shifts everything else down
        course_error.grid_remove()
        add_completed_box_button.grid(row=index + 2, column=0)
        delete_completed_box_button.grid(row=index + 2, column=1)

    add_completed_box_button = tk.Button(frame1, text="Add Another Course", command=add_completed_course_box)
    add_completed_box_button.grid(column=0, row=1)

    # create a button to remove course boxes
    def delete_completed_course_box() -> None:
        """ Deletes last label and course box, and shifts everything else up."""
        index = len(completed_labels) - 1
        # deletes last label
        completed_labels[index].destroy()
        del completed_labels[index]
        # deletes last entry box
        completed_entries[index].destroy()
        del completed_entries[index]
        # shifts everything else up
        course_error.grid_remove()
        add_completed_box_button.grid(row=index + 1, column=0)
        if index == 1:  # if there is only one course box, remove the 'delete course box button'
            delete_completed_box_button.grid_remove()
        else:
            delete_completed_box_button.grid(row=index + 1, column=1)

    delete_completed_box_button = tk.Button(frame1, text="Remove Last Course", command=delete_completed_course_box)

    # Frame 2: For Desired Course
    frame2 = tk.LabelFrame(root, text="What course do you want to complete?", padx=15, pady=15)
    frame2.grid(row=1, column=1)

    # creates a labels and entry boxe for the user to input their desired course
    desired_label = tk.Label(frame2, text="Course Code:")
    desired_entry = tk.Entry(frame2)
    desired_label.grid(row=0, column=0)
    desired_entry.grid(row=0, column=1)

    # create a button to submit courses
    def submit() -> None:
        """ If all the users entries are valid, submit them and display the results."""
        # get all completed courses
        completed_courses = set()
        for key in completed_entries:
            course = completed_entries[key].get().upper()
            if course != '':  # ignore empty course boxes
                if course in (course_dict["course code"] for course_dict in file_contents):
                    completed_courses.add(course)
                else:  # if the course is not a valid course, exit and let the user know
                    course_error.config(text="'" + course + "' is not a valid course.")
                    course_error.grid(row=2, column=0, sticky='W')
                    return

        # get the desired course
        desired_course = desired_entry.get().upper()
        if desired_course == '':  # user must enter a desired course
            course_error.config(text="You must input a desired course.")
            course_error.grid(row=2, column=0, sticky='W')
        elif desired_course in (courses["course code"] for courses in file_contents):
            display_results(desired_course, completed_courses)
        else:  # if the course is not a valid course, exit and let the user know
            course_error.config(text="'" + desired_course + "' is not a valid course.")
            course_error.grid(row=2, column=0, sticky='W')
            return

    submit_button = tk.Button(frame2, text="Submit", command=submit)
    submit_button.grid(row=1, column=0)
    course_error = tk.Label(root)

    # Frame 3: Recommended Path
    frame3 = tk.LabelFrame(root, text="Recommened Path:", padx=15, pady=15, width=60)
    frame3.grid(row=1, column=2)
    starting_label = tk.Label(frame3, text="Submit a course you want to complete for a recommended course path.")
    starting_label.pack()

    def display_results(desired: str, completed: set[str]) -> None:
        """ Generates and draws the recommended path."""
        course_error.grid_remove()
        starting_label.destroy()
        network = get_course_tree(desired, completed)
        tree_drawing.config(text=str(network), justify="left")

    tree_drawing = tk.Label(frame3)
    tree_drawing.pack()

    # Frame 4: Course Search
    frame4 = tk.LabelFrame(root, text="Course Search:", padx=15, pady=15, width=60)
    frame4.grid(row=1, column=3)

    # create labels and an entry box for the user to search courses
    tk.Label(frame4, text="Course Code:").grid()
    course_search_box = tk.Entry(frame4)
    course_search_box.grid(row=0, column=1)

    # create a button to submit courses
    def search() -> None:
        """ If the course is valid, search for it and provide a course overview in another window."""
        # get desired course
        search_course = course_search_box.get().upper()
        if search_course == '':
            course_error.config(text="You must input a course code to search.")
            course_error.grid(row=2, column=0, sticky='W')
        else:
            for course_dict in file_contents:
                if search_course == course_dict["course code"]:
                    course_details = course_dict
                    course_error.grid_remove()

                    # create a new window
                    new_window = tk.Toplevel(root)
                    new_window.title("Course Search: " + search_course)

                    # display the course overview
                    descriptions = {header: tk.Label(new_window) for header in keys}
                    for key in keys:
                        if len(course_details[key]) == 0:
                            value = 'none'
                        elif isinstance(course_details[key], list):
                            value = course_details[key][0]
                        else:
                            value = course_details[key]
                        value = split_string(value)
                        heading = key.replace(" text", 's')
                        descriptions[key].config(text=heading.title() + ': ' + value, justify="left")
                        descriptions[key].pack(anchor="w")

                    exit_window = tk.Button(new_window, text="Exit Course Search", command=new_window.destroy)
                    exit_window.pack()

                    new_window.mainloop()

                    return
                # if the course is not a valid course, let the user know
                course_error.config(text="'" + search_course + "' is not a valid course.")
                course_error.grid(row=2, column=0, sticky='W')

    search_button = tk.Button(frame4, text="Search", command=search)
    search_button.grid(column=0, row=1)

    # list of keys/headers we want to display
    keys = ["course name", "hours", "description", "distribution", "breadth", "mode of delivery",
            "prereq text", "coreq text", "exclusion text", "prep text"]

    # run the tkinter window
    root.mainloop()


if __name__ == '__main__':
    doctest.testmod()
    python_ta.check_all(config={
        'extra-imports': ['tkinter', 'json', 'runner', 'helpers'],  # the names (strs) of imported modules
        'allowed-io': ['run_program'],     # the names (strs) of functions that call print/open/input
        'max-line-length': 120,
        'disable': ['R0914', 'R1702', 'R0915']
    })
