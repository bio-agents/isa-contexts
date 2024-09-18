from json import dump

from isacontexts.constants import JSON_REPORT_PATH
from isacontexts.report.generate_html import generate_report


REPORT = {
    'name': 'ISA context files analysis report',
    'description': 'This reports checks that each schema file has a corresponding context file in each vocabulary. '
                   'It also checks if all fields are properly covered',
    'missing_files': {},
    'missing_fields': {},
    'parse_error': {},
    'empty_fields': {},
    'unresolvable_fields': {}
}


def set_report(report):
    global REPORT
    REPORT = report
    with open(JSON_REPORT_PATH, 'w') as f:
        dump(report, f, indent=4)
    generate_report()
