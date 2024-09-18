from os import path, mkdir
from json import load

from jinja2 import Environment, FileSystemLoader

from isacontexts.constants import JSON_REPORT_PATH, HTML_REPORT_PATH


def get_report_data():
    with open(JSON_REPORT_PATH, 'r') as fp:
        report = load(fp)
    return report


def generate_report():
    here_path = path.abspath(path.dirname(__file__))
    templates_path = path.join(here_path, 'templates')
    with open(path.join(templates_path, 'index.html'), 'r') as fp:
        template_string = fp.read()
    template = Environment(loader=FileSystemLoader(templates_path)).from_string(template_string)
    if not path.exists(HTML_REPORT_PATH):
        mkdir(HTML_REPORT_PATH)
    with open(path.join(HTML_REPORT_PATH, 'index.html'), 'w') as fp:
        fp.write(template.render(get_report_data()))
