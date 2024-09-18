from unittest import TestCase
from os.path import exists, join
from json import load
from requests import get
import logging

from isacontexts.utils import get_vocabularies_path, get_schemas_path
from isacontexts.report.utils import REPORT, set_report

LOGGER = logging.getLogger('ISAContexts')

VOCABULARIES_PATH = get_vocabularies_path()
SCHEMAS_PATH = get_schemas_path()
SCHEMA_FILES = list(SCHEMAS_PATH.keys())


class TestContexts(TestCase):

    @classmethod
    def setUpClass(cls):
        schemas = {}
        for schema_file in SCHEMA_FILES:
            with open(SCHEMAS_PATH[schema_file]) as f:
                schemas[schema_file] = load(f)['properties']
        cls.schemas = schemas

    def test_vocabularies(self):
        for vocabulary_name in VOCABULARIES_PATH:
            for schema_file in SCHEMA_FILES:
                context_filename = 'isa_%s_%s_context.jsonld' % (schema_file, vocabulary_name)
                context_filepath = join(VOCABULARIES_PATH[vocabulary_name], context_filename)
                try:
                    self.context_tester(
                        context_filepath=context_filepath,
                        schema_file=schema_file,
                        vocabulary_name=vocabulary_name,
                        context_filename=context_filename
                    )
                except AssertionError:
                    if vocabulary_name not in REPORT['missing_files']:
                        REPORT['missing_files'][vocabulary_name] = []
                    REPORT['missing_files'][vocabulary_name].append(context_filename)
        set_report(REPORT)

    def context_tester(self, context_filepath, schema_file, vocabulary_name, context_filename):
        self.assertTrue(exists(context_filepath))
        try:
            with open(context_filepath) as f:
                context = load(f)['@context']
                self.coverage_tester(context, schema_file, vocabulary_name, context_filepath)
        except Exception:
            if vocabulary_name not in REPORT['parse_error']:
                REPORT['parse_error'][vocabulary_name] = []
            REPORT['parse_error'][vocabulary_name].append(context_filename)

    def coverage_tester(self, context, schema_file, vocabulary_name, context_filepath):
        fields = [field for field in self.schemas[schema_file] if not field.startswith('@') or field.startswith('_')]
        for field in fields:
            try:
                self.assertIn(field, context)
                self.resolvable(field, context, vocabulary_name, context_filepath, schema_file)
            except AssertionError:
                if vocabulary_name not in REPORT['missing_fields']:
                    REPORT['missing_fields'][vocabulary_name] = {}
                if schema_file not in REPORT['missing_fields'][vocabulary_name]:
                    REPORT['missing_fields'][vocabulary_name][schema_file] = {
                        'fields': [],
                        'filepath': context_filepath
                    }
                REPORT['missing_fields'][vocabulary_name][schema_file]['fields'].append(field)

    def resolvable(self, term, context, vocabulary_name, context_filepath, schema_file):
        context_value = context[term]
        try:
            self.assertIn(type(context_value), (str, dict))
            if type(context_value) == dict:
                self.assertIn('@type', context_value)
                self.assertNotEqual(context_value['@type'], '', msg='@type is empty')
            prefixed_val = (context_value['@type'] if type(context_value) == dict else context_value).split(':')
            self.assertIn(prefixed_val[0], context, msg='Prefix not found in context')
            prefix = context[prefixed_val[0]]
            prefix += '/' if not prefix.endswith('/') else ''
            url = prefix + prefixed_val[1]
            try:
                data = get(url, verify=False)
                if data.status_code != 200:
                    raise AssertionError('URL not resolvable')
            except Exception:
                if vocabulary_name not in REPORT['unresolvable_fields']:
                    REPORT['unresolvable_fields'][vocabulary_name] = {}
                if schema_file not in REPORT['unresolvable_fields'][vocabulary_name]:
                    REPORT['unresolvable_fields'][vocabulary_name][schema_file] = {
                        'fields': [],
                        'filepath': context_filepath
                    }
                REPORT['unresolvable_fields'][vocabulary_name][schema_file]['fields'].append(term)

        except AssertionError:
            if vocabulary_name not in REPORT['empty_fields']:
                REPORT['empty_fields'][vocabulary_name] = {}
            if schema_file not in REPORT['empty_fields'][vocabulary_name]:
                REPORT['empty_fields'][vocabulary_name][schema_file] = {
                    'fields': [],
                    'filepath': context_filepath
                }
            REPORT['empty_fields'][vocabulary_name][schema_file]['fields'].append(term)
