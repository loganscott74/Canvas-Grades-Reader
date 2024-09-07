"""
This script uses the Canvas API to mark graded assignments as read, something that would normally require the long process of opening each assignment individually.

To run:
- Enter your Canvas URL header where it says CANVIS_URL (ex. "https://northeastern.instructure.com")
- Get a token from Canvas and paste it next to token
- Run the program
"""
import json
import requests
from types import SimpleNamespace

# Canvas URL
CANVIS_URL = "ENTER CANVAS URL HERE"
"""Your school's/institution's Canvas url

Example: "https://northeastern.instructure.com"
"""

# Canvas access token
TOKEN = "ENTER TOKEN HERE"
"""You Canvas access token

To get an access token:
- Go to Account -> Settings
- Scroll down to Approved Integrations
- Hit "New Access Token" and create a new token
- Copy and past the token here
"""

authorize = { "Authorization" : "Bearer " + TOKEN}
"""The header for all API requests with the token. Required."""

course_request_url = CANVIS_URL + "/api/v1/courses/"
"""The Canvas URL with the begining of an API request"""

# Get the user's course list
def get_courses() -> any:
    """Get the user's course list
    
    Returns
    -------
    any
        A SimpleNamespace of all the courses the user is in
    """

    course_request = requests.get(course_request_url + "?per_page=100", headers=authorize)
    return json.loads(course_request.text, object_hook=lambda d: SimpleNamespace(**d))

# Gets the list of assignments for the given course
def get_assignments(course_id: int) -> any:
    """Gets the list of assignments for the given course
    
    Parameters
    ----------
    course_id: int
        The ID of the course to get the assignments for 
    
    Returns
    -------
    any
        A SimpleNamespace json containing all information of the course
    """

    assignments_request = requests.get(course_request_url + str(course_id) + "/assignments/?per_page=100", headers=authorize, params={"include" : "submission"})
    if assignments_request.status_code >= 200 and assignments_request.status_code < 300:
        return json.loads(assignments_request.text, object_hook=lambda d: SimpleNamespace(**d))
    else:
        # Runs if the assignments for a course was not found. Fixes issue were unauthorized classes (due to withdraws) would lead to a crash
        print("WARNING: Failed to load assignments for course", course_id, "Error:", assignments_request.text, assignments_request.status_code)
        return {}

# Marks the given assignment for the given course ID as read
def mark_assignment_read(course_id: int, assignment: any):
    """Marks the given assignment for the given course ID as read
    
    Parameters
    ----------
    course_id: int
        The id for the course containing these assignments
    assignment: any
        A list of the assignments in this course
    """

    if (assignment.has_submitted_submissions):
        assignment_id = assignment.id
        submission_id = assignment.submission.user_id
        read_url = course_request_url + str(course_id) + "/assignments/" + str(assignment_id) + "/submissions/" + str(submission_id) + "/read"
        requests.put(read_url, headers=authorize)


def main():
    print("Getting courses...")
    courses = get_courses()

    # For each course, get all of the assignments
    for course in courses:
        if hasattr(course, 'name'):
            print("Getting assignments for", course.name, "( id:", course.id, ")")
        else:
            # If no course name found, than the user does not have access to the course
            print("No permission to access course with id: (", course.id, ")Skipping course")
            continue

        assignments = get_assignments(course.id)

        # For each assignment, mark it as read
        for assignment in assignments:
            mark_assignment_read(course.id, assignment)
    print("Done")


if __name__ == '__main__':
    main()