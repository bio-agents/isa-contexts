from unittest import TestCase
from os import walk
from os.path import join
from json import load
from pandas import DataFrame, ExcelWriter

from isacontexts.utils import get_vocabularies_path
from isacontexts.constants import MAPPING_PATH, MAPPING_HEADERS, PREDICATE, MAPPING_JUSTIFICATION

VOCABULARIES_PATH = get_vocabularies_path()


class TestMapping(TestCase):

    @classmethod
    def setUpClass(cls):
        vocab = {}
        for vocabulary, vocabulary_path in VOCABULARIES_PATH.items():
            vocab[vocabulary] = {}
            for file in walk(vocabulary_path):
                for filename in file[2]:
                    if filename.endswith('.jsonld') and 'allinone' not in filename:
                        with open(join(vocabulary_path, filename)) as f:
                            isa_object_name = filename.replace('isa_', '')\
                                .replace('_context.jsonld', '')\
                                .replace(vocabulary, '')\
                                .replace('_', '')
                            context_content = load(f)['@context']
                            for field_name, field_val in context_content.items():
                                if not field_name.startswith('@') and field_name not in [vocabulary, 'xsd', 'isa']:
                                    try:
                                        if type(field_val) == dict:
                                            if field_val['@id'] == '':
                                                continue
                                            vocab[vocabulary][field_name] = field_val['@id']
                                        else:
                                            vocab[vocabulary][field_name] = field_val
                                    except Exception:
                                        continue
        cls.vocab = vocab

    def test_create_mapping(self):
        mapping = []
        for vocab, context in self.vocab.items():
            for field, field_val in context.items():
                for mapped_vocab, mapped_context in self.vocab.items():
                    if mapped_vocab != vocab:
                        if field in mapped_context:
                            mapping.append([
                                field_val,
                                PREDICATE,
                                mapped_context[field],
                                MAPPING_JUSTIFICATION,
                                field,
                                field
                            ])
        df = DataFrame(mapping, columns=MAPPING_HEADERS)
        with ExcelWriter(MAPPING_PATH, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
