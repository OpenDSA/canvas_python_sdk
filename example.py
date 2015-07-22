from canvas_sdk.methods import courses, modules, assignments
from canvas_sdk import RequestContext
import json

oauth_token = '7~98d8KnPbCj7wnA3GLyHIvh4yxHz7t2U6SPp7OLdvscWSN82qCnZbEWebFJVEb0b3'
canvas_url = 'https://canvas.instructure.com/api'

course_id = 951807

# init the request context
request_context = RequestContext(oauth_token, canvas_url)

results = modules.create_module(request_context, course_id, "Sorting Chapter")
module_id = results.json()["id"]
# print json.dumps(results.json())

results = modules.create_module_item(
    request_context, course_id, module_id, 'SubHeader',
    module_item_content_id=None, module_item_title="Quicksort Module",
    module_item_indent=0)
item_id = results.json()["id"]
# print json.dumps(results.json())

results = assignments.create_assignment(
    request_context, course_id,
    "Quicksort Slide 1",
    assignment_submission_types="external_tool",
    assignment_external_tool_tag_attributes={
        "url": "https://ltitest.herokuapp.com/lti_tool?problem_type=module&problem_url=CS3114/html/&short_name=Quicksort-01&JOP-lang=en&JXOP-feedback=continuous&JXOP-fixmode=fix&JXOP-code=processing&JXOP-debug=true"},
    assignment_points_possible=2, assignment_description="Quicksort Silde 1")
assignment_id = results.json()["id"]
# print json.dumps(results.json())

results = modules.create_module_item(
    request_context, course_id, module_id, 'Assignment', module_item_content_id=assignment_id, module_item_indent=1)
print json.dumps(results.json())

# for idx, course in enumerate(results.json()):
#      print "course %d has data %s" % (idx, course)