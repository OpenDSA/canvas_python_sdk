from canvas_sdk.methods import courses, modules, assignments
from canvas_sdk import RequestContext
from pprint import pprint
import json, collections

oauth_token = '7~98d8KnPbCj7wnA3GLyHIvh4yxHz7t2U6SPp7OLdvscWSN82qCnZbEWebFJVEb0b3'
canvas_url = 'https://canvas.instructure.com/api'
course_id = 951807

# init the request context
request_context = RequestContext(oauth_token, canvas_url)

with open('CS3114_orig.json') as data_file:
    config_data = json.load(data_file, object_pairs_hook=collections.OrderedDict)

# print(type(config_data))
book_titile = config_data["title"]
# change the course title

chapters = config_data["chapters"]
# print(type(chapters))

for chapter in chapters:
    chapter_obj = chapters[str(chapter)]
    # print(str(chapter))
    # OpenDSA chapters will map to canvas modules
    results = modules.create_module(request_context, course_id, str(chapter)+" Chapter")
    module_id = results.json()["id"]
    for module in chapter_obj:
        module_obj = chapter_obj[str(module)]
        # print module_obj["long_name"]
        # OpenDSA module header will map to canvas text header
        results = modules.create_module_item(
            request_context, course_id, module_id, 'SubHeader',
            module_item_content_id=None, module_item_title=module_obj["long_name"]+" Module",
            module_item_indent=0)
        item_id = results.json()["id"]
        exercises = module_obj["exercises"]
        if bool(exercises):
            exercise_counter = 1
            for exercise in exercises:
                exercise_obj = exercises[str(exercise)]
                # pprint(exercise_obj)
                print(str(exercise_counter).zfill(2))+" "+exercise_obj["long_name"]
                # OpenDSA exercises will map to canvas assignments
                results = assignments.create_assignment(
                    request_context, course_id,
                    exercise_obj["long_name"],
                    assignment_submission_types="external_tool",
                    assignment_external_tool_tag_attributes={
                        "url": "https://ltitest.herokuapp.com/lti_tool?problem_type=module&problem_url=CS3114/html/&short_name=Quicksort-"+str(exercise_counter).zfill(2)},
                    assignment_points_possible=exercise_obj["points"],
                    assignment_description=exercise_obj["long_name"])
                assignment_id = results.json()["id"]

                # add assignment to module
                results = modules.create_module_item(
                    request_context, course_id, module_id, 'Assignment', module_item_content_id=assignment_id, module_item_indent=1)
                # print json.dumps(results.json())
                exercise_counter += 1

