"""CSC111 Final Project: Simplifying the UofT Course Selection Process

Description
===============================
This is the main file, which uses tkinter to display a window and interact with the user.

Copyright and Usage Information
===============================
This file is Copyright (c) 2023 Noah Black, Nikita Goncharov and Adam Pralat.
"""
from tkinter import *
import json
from runner import run
from helpers import split_string


def run_program():
    """
    Creates a tkinter window which allows the user to input the course codes of the courses they have already
    completed, as well as the course they want to complete (desired course).
    Once they submit their courses, they will get back a breif course overview
    and a tree diagram of the recommended course path.
    """
    # load course data
    with open('../data-processing/courses_clean.json') as file:
        file_contents = json.load(file)

    # create the tkinter window
    root = Tk()
    root.title("Simplifying the Course Selection Process")

    # Introduction
    Label(root, text="Welcome to the UofT Course Selection Simplifier!\
    \nThis program takes in the courses that a student wants to complete, as well as the courses the student has\
 already completed (if none, leave the boxes empty),\nand recommends the shortest sequence of courses for the student\
 so that they can complete all required prerequisites and corequisites for their desired course.\
    \nPlease refer to the project report for more details.").grid(row=0, column=0, columnspan=4)

    """ Frame 1: For Completed Courses """
    frame1 = LabelFrame(root, text="What courses have you completed?", padx=15, pady=15)
    frame1.grid(row=1, column=0)
    # create labels and entry boxes for the user to input completed courses
    labels = {0: Label(frame1, text="Course Code:")}
    entries = {0: Entry(frame1)}
    labels[0].grid(row=0, column=0)
    entries[0].grid(row=0, column=1)

    # create a button to add more courses
    def add_course_box():
        """ Creates a new label and entry box, and shifts everything else down. """
        index = len(labels)
        # creates new label
        labels[index] = Label(frame1, text="Course Code:")
        labels[index].grid(row=index + 1, column=0)
        # creates new entry box
        entries[index] = Entry(frame1)
        entries[index].grid(row=index + 1, column=1)
        # shifts everything else down
        course_error.grid_remove()
        add_course_box_button.grid(row=index + 2, column=0)
        delete_course_box_button.grid(row=index + 2, column=1)

    add_course_box_button = Button(frame1, text="Add Another Course", command=add_course_box)
    add_course_box_button.grid(column=0, row=1)

    # create a button to remove course boxes
    def delete_course_box():
        """ Deletes last label and course box, and shifts everything else up. """
        index = len(labels) - 1
        # deletes last label
        labels[index].destroy()
        del labels[index]
        # deletes last entry box
        entries[index].destroy()
        del entries[index]
        # shifts everything else up
        course_error.grid_remove()
        add_course_box_button.grid(row=index + 1, column=0)
        if index == 1:  # If there is only one course box, remove the 'delete course box button'
            delete_course_box_button.grid_remove()
        else:
            delete_course_box_button.grid(row=index + 1, column=1)

    delete_course_box_button = Button(frame1, text="Remove last course", command=delete_course_box)

    """ Frame 2: For Desired Course """
    frame2 = LabelFrame(root, text="What course do you want to complete?", padx=15, pady=15)
    frame2.grid(row=1, column=1)
    # create labels and an entry box for the user to input their desired course
    Label(frame2, text="Course Code:").grid()
    desired_course_box = Entry(frame2)
    desired_course_box.grid(row=0, column=1)

    # create a button to submit courses
    def submit():
        """ If all the users entries are valid, submit them and display the results. """
        # get all completed courses
        completed_courses = set()
        for key in entries:
            course = entries[key].get().upper()
            if course != '':  # Ignore empty course boxes
                if course in (course_dict["course code"] for course_dict in file_contents):
                    completed_courses.add(course)
                else:  # If the course is not a valid course, exit and let the user know
                    course_error.config(text="'" + course + "' is not a valid course.")
                    course_error.grid(row=2, column=0, sticky='W')
                    return

        # get desired course
        desired_course = desired_course_box.get().upper()
        if desired_course == '':
            course_error.config(text="You must input a desired course.")
            course_error.grid(row=2, column=0, sticky='W')
        else:
            if any(desired_course == courses["course code"] for courses in file_contents):
                course_error.grid_remove()
                display_results(completed_courses, desired_course)
                return
            # If the course is not a valid course, let the user know
            course_error.config(text="'" + desired_course + "' is not a valid course.")
            course_error.grid(row=2, column=0, sticky='W')

    submit_button = Button(frame2, text="Submit", command=submit)
    submit_button.grid(column=0, row=1)
    exit_button = Button(frame2, text="Exit Program", command=root.destroy)
    exit_button.grid(column=1, row=1)
    course_error = Label(root)

    """ Frame 3: Recommened Path """
    frame3 = LabelFrame(root, text="Recommened Path:", padx=15, pady=15, width=60)
    frame3.grid(row=1, column=2)
    starting_label = Label(frame3, text="Submit a course you want to complete for a recommended course path.")
    starting_label.pack()

    def display_results(completed: set[str], desired: str):
        """ Creates a new course network from the courses provided by the user,
        and draws the recommended path diagram.
        """
        network = run(desired, completed)

        starting_label.destroy()
        tree_drawing.config(text=str(network), justify="left")
        tree_drawing.pack()

    tree_drawing = Label(frame3)

    """ Frame 4: Course Search """
    frame4 = LabelFrame(root, text="Course Search:", padx=15, pady=15, width=60)
    frame4.grid(row=1, column=3)
    # create labels and an entry box for the user to search courses
    Label(frame4, text="Course Code:").grid()
    course_search_box = Entry(frame4)
    course_search_box.grid(row=0, column=1)

    # create a button to submit courses
    def search():
        """ If all the course is valid, search for it and provide a course overview in another window. """
        # get desired course
        search_course = course_search_box.get().upper()
        if search_course == '':
            course_error.config(text="You must input a desired course.")
            course_error.grid(row=2, column=0, sticky='W')
        else:
            for i in range(len(file_contents)):
                if search_course == file_contents[i]["course code"]:
                    course_details = file_contents[i]
                    course_error.grid_remove()

                    # create a new window
                    new_window = Toplevel(root)
                    new_window.title("Course Search: " + search_course)

                    # displays the course overview
                    descriptions = {key: Label(new_window) for key in keys}
                    for key in keys:
                        if len(course_details[key]) == 0:
                            value = 'none'
                        elif isinstance(course_details[key], list):
                            value = course_details[key][0]
                        else:
                            value = course_details[key]
                        value = split_string(value)
                        header = key.replace(" text", 's')
                        descriptions[key].config(text=header.title() + ': ' + value, justify="left")
                        descriptions[key].pack(anchor="w")

                    exit_window = Button(new_window, text="Exit Course Search", command=new_window.destroy)
                    exit_window.pack()

                    new_window.mainloop()

                    return
                # If the course is not a valid course, let the user know
                course_error.config(text="'" + search_course + "' is not a valid course.")
                course_error.grid(row=2, column=0, sticky='W')

    search_button = Button(frame4, text="Search", command=search)
    search_button.grid(column=0, row=1)

    # list of keys/headers we want to display
    keys = ["course name", "hours", "description", "distribution", "breadth", "mode of delivery",
            "prereq text", "coreq text", "exclusion text", "prep text"]

    # run the tkinter window
    root.mainloop()


if __name__ == '__main__':
    run_program()
