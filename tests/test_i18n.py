import unittest
from string import Formatter
from i18n import STRINGS, LANGUAGES, CATALOG, DEFAULT_LANGUAGE, tr

class I18nTests(unittest.TestCase):
    def test_same_keys_all_languages(self):
        expected = set(STRINGS['en'])
        for lang in LANGUAGES:
            self.assertEqual(set(STRINGS[lang]), expected, lang)

    def test_format_placeholders_match(self):
        def fields(value):
            return {name for _, name, _, _ in Formatter().parse(value) if name is not None}
        for key, value in STRINGS['en'].items():
            for lang in LANGUAGES:
                self.assertEqual(fields(STRINGS[lang][key]), fields(value), (lang, key))

    def test_catalog_complete_en_de(self):
        from engine import CONDITIONS, ACTIONS
        expected = set(CONDITIONS) | set(ACTIONS)
        for lang in ('en', 'de'):
            self.assertEqual(set(CATALOG[lang]), expected)

    def test_default_language(self):
        self.assertEqual(DEFAULT_LANGUAGE, 'en')
        self.assertEqual(tr('not-a-language', 'tab_about'), 'About')
