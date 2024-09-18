from os import path

HERE_PATH = path.abspath(path.dirname(__file__))
VOCAB_PATH = path.join(HERE_PATH, '..', 'contexts')
SCHEMAS_PATH = path.join(HERE_PATH, 'resources', 'schemas')

JSON_REPORT_PATH = path.join(HERE_PATH, 'resources', 'report.json')
HTML_REPORT_PATH = path.join(HERE_PATH, '..',  'dist')

MAPPING_PATH = path.join(HERE_PATH, '..', 'contexts', 'mapping.xlsx')
MAPPING_HEADERS = ["subject_id", "predicate_id", "object_id", "mapping_justification", "subject_label", "object_label"]
PREDICATE = "skos:exactMatch"
MAPPING_JUSTIFICATION = "semapv:ManualMappingCuration"
