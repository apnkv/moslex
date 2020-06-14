import re
import os
import sys
import logging
import pandas as pd
import operator
import bibtexparser
from functools import reduce
from collections import defaultdict
from slugify import slugify

from .util import get_lang_location_and_status
from .xlrd2pd import read_formatted_excel, to_ipa

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)-15s]  %(message)s')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)

ET_AL = 'et al'
SPLITTER_CHAR = '.'


def slugify_source_reference(ref):
    ref = ref.replace(ET_AL, '').replace(',', '').replace(' ', '').replace('&', '')
    return slugify(ref, lowercase=False)


def split_leading_sources(s):
    """
    Correctly splits a comment cell value into leading sources and the rest.
    Example:
    `Herault 1983: 44. Literally: 'head-hair'. Quoted as ór-f in [Kouadio 1983: 31].` ->
    ('Herault 1983: 44', 'Literally: 'head-hair'. Quoted as ór-f in [Kouadio 1983: 31].')

    :param s: form comment with leading source references
    :return: a tuple (references, rest of the comment)
    """

    splitter = SPLITTER_CHAR if SPLITTER_CHAR != '.' else '\\.'
    split_idx = next(re.finditer(rf'(?<!{ET_AL}){splitter}', s)).start()

    # char at split_idx omitted on purpose
    sources_candidate, rest_candidate = s[:split_idx], s[split_idx + 1:]

    # does the string contain actual source references?
    if len(sources_candidate.split(';')[0].split(':')) != 2:
        return '', f'{sources_candidate}{SPLITTER_CHAR}{rest_candidate}'
    else:
        return sources_candidate.strip(), rest_candidate.strip()


def parse_sources(s):
    """
    Takes in a semicolon-separated sources string. Each source may or may not contain
    page references, in which case they should go after a colon after the year,
    separated with commas. Single-page references become ints, multipage ones are
    treated as strings. Incorrect ints without dashes become volume numbers. Example:

    `Gruber 1975; Collins 2001a: I, 461, 505-509` ->
    [
        {
            'ref': 'Gruber1975',
            'pages': [],
        },
        {
            'ref': 'Collins2001a',
            'pages': [461, '505-509'],
            'volume': 'I',
        },
    ]

    :param s: sources as one string
    :return: list of dicts {'ref': str, 'pages': list, 'volume': Optional[str]}
    """
    source_candidates = [x.strip() for x in s.split(';')]
    sources = []

    for source in source_candidates:
        split_source = source.split(':')
        print(split_source)
        if len(split_source) == 2:
            ref, _pages = [x.strip() for x in split_source]
        elif len(split_source) == 1:
            ref, _pages = split_source[0], ''
        else:
            raise ValueError(f'Malformed source `{source}`.')

        ref = slugify_source_reference(ref)

        source_dict = {'repl': source}
        pages = []
        if _pages:
            for page_ref in _pages.split(','):
                page_ref = re.sub(r' \(#[0-9]+\)', '', page_ref)
                if '-' in page_ref:  # TODO: alt+0150
                    pages.append(page_ref.strip())
                else:
                    try:
                        pages.append(int(page_ref))
                    except ValueError:
                        # logger.warning(f'WARNING: treating \'{page_ref}\' in: "{source}" as volume number.')
                        source_dict['volume'] = page_ref

        source_dict.update({'ref': ref, 'pages': pages})
        sources.append(source_dict)

    return sources


def parse_language_description(description: str) -> dict:
    """
    Parses one GLD language description string, e. g.:
    `Compiled and annotated by G. Starostin. {Sources: Herault 1983.} {Ethnologue: aba.}`
    becomes
    {
        'author': 'G. Starostin',
        'sources': ['Herault1983'],
        'ethnologue': 'aba'
    }
    :param description: correctly formed language description string
    :return: language meta as a dictionary
    """
    # TODO: make sure that all attributes are present
    result = {}

    # TODO: parse proto languages
    attrs = re.findall(r'{[^{^\}]*\}', description)
    author = description[description.find('by '):description.find('{')].strip()[3:]
    if author.endswith('.'):
        author = author[:-1]
    result['author'] = author

    def get_key(s):
        return s[:s.find(':')][1:].lower()

    def get_value(s, key):
        s = s[s.find(':') + 1:-1]
        if s.endswith('.'):
            s = s[:-1]
        s = s.strip()
        if key == 'sources':
            sources = parse_sources(s)
            sources = [src['ref'] for src in sources]
            return sources
        else:
            return s

    keys = [get_key(attr) for attr in attrs]
    values = [get_value(attr, key) for attr, key in zip(attrs, keys)]

    result.update({key: value for key, value in zip(keys, values)})
    return result


def parse_notes(notes, dataset_sources, full_comment=True, try_parse_sources=False):
    if pd.isnull(notes):
        return [], ''

    sources_str, rest_notes = split_leading_sources(notes)
    sources = parse_sources(sources_str) if try_parse_sources else []

    common_sources = []
    ad_hoc_sources = []
    for src in sources:
        if src['ref'] in dataset_sources:
            common_sources.append(src)
        else:
            ad_hoc_sources.append(src)

    def join_ad_hoc_sources():
        if len(ad_hoc_sources) > 1:
            parts = '; '.join([src['repl'] for src in ad_hoc_sources])
        else:
            parts = ad_hoc_sources[0]['repl'] if len(ad_hoc_sources) == 1 else ''
        if len(parts) > 0:
            parts += '.'
        if parts:
            parts = [parts]
        else:
            parts = []
        return parts

    note_parts = join_ad_hoc_sources()
    if rest_notes:
        note_parts.append(rest_notes)

    return sources, ' '.join(note_parts) if not full_comment else notes


def slugify_language(s):
    to_replace = 'ǁǂ!_ǀ\''
    replace_by = ('ll', 'H', '1', 'L', 'I', 'i')
    replacements = [[src, dst] for (src, dst) in zip(to_replace, replace_by)]

    return slugify(s, lowercase=False, separator='', replacements=replacements)


def parse_form_row(row, languages, sources, try_parse_sources=False):
    row = row[1]
    result = []
    for language, lang_data in languages.items():
        form_sources, notes = parse_notes(row[lang_data['name'] + ' notes'], sources,
                                          try_parse_sources=try_parse_sources)
        result.append({
            # 'ID': language + str(row['Number']),
            'language': language,
            'gld_word_id': row['Number'],
            'form': row[lang_data['name']],
            'ipa': to_ipa(row[lang_data['name']]) if not pd.isnull(row[lang_data['name']]) else row[lang_data['name']],
            'comment': notes,
            'sources': form_sources,
            'cognate_class': row[lang_data['name'] + ' #']
        })
    return result


def parse_gld_xls(xls_path, bib_path=None, try_parse_sources=False):
    df = read_formatted_excel(xls_path)
    lang_cols = [x for x in list(df.columns) if x.lower() not in ('number', 'word')]
    languages = dict()

    for col in lang_cols:
        aux_col_suffixes = (' #', ' notes', ' etymology')
        if not any(col.endswith(suffix) for suffix in aux_col_suffixes):
            attributes = parse_language_description(df.loc[0, col.strip() + ' notes'])
            slug = slugify_language(col.strip())
            languages[slug] = attributes
            languages[slug].update(
                get_lang_location_and_status(attributes.get('glottolog', None), attributes.get('ethnologue', None))
            )
            languages[slug]['name'] = col.strip()

    source_refs = reduce(operator.add, [languages[lang]['sources'] for lang in languages.keys()], [])
    unique_source_refs = set(slugify_source_reference(ref) for ref in source_refs)

    sources = {key: {} for key in unique_source_refs}
    if not bib_path:
        candidate_path = os.path.splitext(xls_path)[0] + '.bib'
        if os.path.exists(candidate_path):
            bib_path = candidate_path
    if bib_path:
        with open(bib_path, 'r') as bibfile:
            _bib = bibtexparser.load(bibfile).entries
        bib = {}
        for item in _bib:
            ref = item['ID']
            del item['ID']
            bib[ref] = item
        for source in sources.keys():
            if source not in bib:
                logger.warning(f'Source `{source}` is not present in {bib_path}.')
            else:
                sources[source] = bib[source]

    forms = []
    rows = df.iterrows()
    next(rows)
    for row in rows:
        forms.extend(parse_form_row(row, languages, sources, try_parse_sources=try_parse_sources))
    cognates = defaultdict(lambda: defaultdict(list))
    for i, form in enumerate(forms):
        cognates[form['gld_word_id']][form['cognate_class']].append(i)
    return {
        'languages': languages,
        'sources': sources,
        'forms': forms,
        'cognates': dict({key: dict(value) for key, value in cognates.items()})
    }
