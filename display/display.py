"""
Creates a tkinter window which allows the user to input the course codes of the courses they have already
completed, as well as the course they want to complete (desired course).
"""
from tkinter import *
from tkinter import ttk
import json

# create a list of all possible courses
all_courses = []
with open('../data-processing/courses_clean.json') as file:
    file_contents = json.load(file)

for course_dict in file_contents:
    all_courses.append(course_dict["course code"])

# create the tkinter window
root = Tk()
# root.attributes('-fullscreen', True)
root.title("Simplifying the Course Selection Process")

""" Introduction """
Label(root, text="\
Welcome to ...\
Please refer to the project report for more details.").grid(row=0, column=0)

""" Frame 1: For completed courses. """
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


add_course_box_button = Button(frame1, text="Add another course", command=add_course_box)
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


""" Frame 2: For desired course. """
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
    completed_courses = []
    for key in entries:
        course = entries[key].get()
        if course != '':  # Ignore empty course boxes
            if course in all_courses:
                completed_courses.append(course)
            else:  # If the course is not a valid course, exit and let the user know
                course_error.config(text="'" + course + "' is not a valid course.")
                course_error.grid(row=2, column=0, sticky='W')
                return

    # get desired course
    desired_course = desired_course_box.get()
    if desired_course == '':
        course_error.config(text="You must input a desired course.")
        course_error.grid(row=2, column=0, sticky='W')
    elif desired_course not in all_courses:
        course_error.config(text="'" + desired_course + "' is not a valid course.")
        course_error.grid(row=2, column=0, sticky='W')

    # If all courses are valid, display the results
    else:
        display_results(completed_courses, desired_course)


submit_button = Button(frame2, text="Submit", command=submit)
submit_button.grid(column=0, row=1)
exit_button = Button(frame2, text="Exit Program", command=root.destroy)
exit_button.grid(column=1, row=1)
course_error = Label(root)

""" Frame 3: Results."""
frame3 = LabelFrame(root, text="Recommended Course Path:", padx=15, pady=15)
frame3.grid(row=1, column=2)
starting_label = Label(frame3, text="Submit a course you want to complete for a recommended\
 \n course path (based on courses that you have completed) \nas well as a brief course description!")
starting_label.grid(row=0, column=0)


def display_results(completed: list[str], desired: str):
    """ TODO """
    starting_label.destroy()
    recommended_path.grid_remove()
    tree_drawing.grid_remove()
    description.grid_remove()
    recommended_path.config(text="We recommend taking the following courses:" + get_path(completed, desired))
    recommended_path.grid(row=0, column=0)
    tree_drawing.config(text=draw_tree())
    tree_drawing.grid(row=1, column=0)
    description.config(text="Course description:" + get_description(desired))
    description.grid(row=2, column=0)


recommended_path = Label(frame3)
description = Label(frame3)
tree_drawing = Label(frame3)

# run the tkinter window
root.mainloop()
