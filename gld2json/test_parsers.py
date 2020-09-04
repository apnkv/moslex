import unittest
import parsers


class TestSlugifySourceReference(unittest.TestCase):
    def test_spaces(self):
        self.assertEqual(parsers.slugify_source_reference('Patte 2011'), 'Patte2011')
        self.assertEqual(parsers.slugify_source_reference('Van Breugel 2008'), 'VanBreugel2008')

    def test_multiple_authors(self):
        self.assertEqual(parsers.slugify_source_reference('Johnson & Johnson 2005'), 'JohnsonJohnson2005')
        self.assertEqual(parsers.slugify_source_reference('Johnson & Johnson & Koch 2005'), 'JohnsonJohnsonKoch2005')
        self.assertEqual(parsers.slugify_source_reference('Johnson & de Vries 1895'), 'JohnsondeVries1895')

    def test_comma_separated(self):
        self.assertEqual(parsers.slugify_source_reference('Johnson, Johnson 2007'), 'JohnsonJohnson2007')

    def test_et_al(self):
        self.assertEqual(parsers.slugify_source_reference('Hamm et al. 2003'), 'Hamm2003')


class TestSourceParsers(unittest.TestCase):
    def test_split_leading_sources(self):
        self.assertEqual(parsers.split_leading_sources(
            'Enrico 2005: 1495, 1892. A qʼál.'
        ), ('Enrico 2005: 1495, 1892', 'A qʼál.'))

        self.assertEqual(parsers.split_leading_sources(
            '''ǂHoan-Cornell. Reduplicated variant; the non-reduplicated variant is quoted in [Honken 1977: 158] after J. Gruber's notes as !ʰǒ, pl. !ʰẽ. '''
        ), ('', '''ǂHoan-Cornell. Reduplicated variant; the non-reduplicated variant is quoted in [Honken 1977: 158] after J. Gruber's notes as !ʰǒ, pl. !ʰẽ. '''))

        self.assertEqual(parsers.split_leading_sources(
            '''Gruber 1975: 4; Collins 2001a: 461. Quoted as ciː in [Traill 1973: 31].'''
        ), ('Gruber 1975: 4; Collins 2001a: 461',
            '''Quoted as ciː in [Traill 1973: 31].'''))

        self.assertEqual(parsers.split_leading_sources(
            '''Alfira et al. 2013: 10. Not attested in Thelwall's materials. Cf. kidi 'female breast' in [Thelwall 1981a: 93, 100].'''
        ), ('Alfira et al. 2013: 10',
            '''Not attested in Thelwall's materials. Cf. kidi 'female breast' in [Thelwall 1981a: 93, 100].'''))

        self.assertEqual(parsers.split_leading_sources(
            '''Alfira et al. 2013: 10; de Vries et al. 2005: 109. Not attested in Thelwall's materials. Cf. kidi 'female breast' in [Thelwall 1981a: 93, 100].'''
        ), ('Alfira et al. 2013: 10; de Vries et al. 2005: 109',
            '''Not attested in Thelwall's materials. Cf. kidi 'female breast' in [Thelwall 1981a: 93, 100].'''))

    def test_parse_sources(self):
        # one source, several pages
        self.assertEqual(parsers.parse_sources(
            '''Enrico 2005: 1128, 1664-65, 2056'''
        ), [{'ref': 'Enrico2005', 'pages': [1128, '1664-65', 2056]}])

        # multiple sources
        self.assertEqual(parsers.parse_sources(
            '''Gruber 1975: 4; Collins 2001a: 461'''
        ), [{'ref': 'Gruber1975', 'pages': [4]}, {'ref': 'Collins2001a', 'pages': [461]}])

        # missing pages
        self.assertEqual(parsers.parse_sources(
            '''Gruber 1975; Collins 2001a: 461'''
        ), [{'ref': 'Gruber1975', 'pages': []}, {'ref': 'Collins2001a', 'pages': [461]}])

        # volume number
        self.assertEqual(parsers.parse_sources(
            '''Gruber 1975; Collins 2001a: I, 461'''
        ), [{'ref': 'Gruber1975', 'pages': []}, {'ref': 'Collins2001a', 'volume': 'I', 'pages': [461]}])


class TestParseNotes(unittest.TestCase):
    def test_parse_notes(self):
        pass


class TestSlugifyLanguage(unittest.TestCase):
    def test_slugify_obscure_language(self):
        self.assertEqual(parsers.slugify_language('ǂKhomani'), 'HKhomani')
        self.assertEqual(parsers.slugify_language('ǁNg!ke'), 'llNg1ke')
        self.assertEqual(parsers.slugify_language('ǀ\'Auni'), 'IiAuni')
        self.assertEqual(parsers.slugify_language('Proto-!Wi'), 'Proto1Wi')


if __name__ == '__main__':
    unittest.main()
