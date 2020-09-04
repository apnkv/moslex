from __future__ import unicode_literals
import sys
import json
import operator
from slugify import slugify
from collections import defaultdict

from clld.scripts.util import initializedb, Data
from clld.db.meta import DBSession
from clld.db.models import common

import moslex
from moslex import models

mock_language = {'model': 'starling.languoid',
                 'pk': 389,
                 'fields': {'name': 'Upper Inlet Tanaina',
                            'author': None,
                            'year_collected': None,
                            'rich_description': '<b>kek</b>',
                            'parent': None,
                            'type': 3,
                            'status': 'moribund',
                            'latitude': '60.471200',
                            'longitude': '-150.759000',
                            'macroarea': None,
                            'glottocode': 'tana1289',
                            'ethnologue_code': 'tfn',
                            'iso_code': None,
                            'reference': None,
                            'taxonomy': 'Dene-Caucasian -> Na-Dene -> Athabaskan',
                            'slug': 'UpperInletTanaina',
                            'lft': 18,
                            'rght': 19,
                            'tree_id': 24,
                            'level': 0
                            }
                 }


def get_languoid_key_(_id):
    return f'languoid-{_id}'


def add_languoids(data, languoids: list):
    converted_pk = dict()
    languoids = sorted(languoids, key=lambda x: operator.itemgetter('level')(x['fields']))

    current_pk = 0

    for languoid in languoids:
        fields = languoid['fields']
        old_pk = languoid['pk']

        key_ = get_languoid_key_(old_pk)

        name = fields['name']
        parent = fields.get('parent', None)
        latitude = fields.get('latitude', None)
        longitude = fields.get('longitude', None)
        rich_description = fields.get('rich_description', None)
        glottocode = fields.get('glottocode', None)
        ethnologue_code = fields.get('ethnologue_code', None)
        nex_url = fields.get('nex_url', None)
        description_file_url = fields.get('description_file_url', None)

        add_kwargs = {
            'name': name,
            'id': slugify(name),
        }

        if parent is not None:
            print(parent)
            add_kwargs['parent_pk'] = converted_pk[parent]

        if latitude is not None and longitude is not None:
            add_kwargs['latitude'] = latitude
            add_kwargs['longitude'] = longitude

        if rich_description is not None:
            add_kwargs['description'] = rich_description
            add_kwargs['markup_description'] = rich_description

        if glottocode is not None:
            add_kwargs['glottocode_'] = glottocode

        if ethnologue_code is not None:
            add_kwargs['ethnologue_code'] = ethnologue_code

        if nex_url is not None:
            add_kwargs['nex_url'] = nex_url

        if description_file_url is not None:
            add_kwargs['description_file_url'] = description_file_url

        add_kwargs['level'] = [
            models.LanguoidLevel.superfamily,
            models.LanguoidLevel.family,
            models.LanguoidLevel.group,
            models.LanguoidLevel.language,
        ][fields.get('level', 3)]

        instance = data.add(models.Languoid, key_, **add_kwargs)

        if glottocode is not None:
            identifier = data.add(models.Identifier, f'{key_}-glottocode',
                                  type=models.IdentifierType.glottolog.value,
                                  name=glottocode)
            DBSession.add(common.LanguageIdentifier(language=instance, identifier=identifier))

        if ethnologue_code is not None:
            identifier = data.add(models.Identifier, f'{key_}-ethnologue',
                                  type=models.IdentifierType.glottolog.value,
                                  name=ethnologue_code)
            DBSession.add(common.LanguageIdentifier(language=instance, identifier=identifier))

        converted_pk[old_pk] = instance.pk
        current_pk += 1


def get_concept_key_(_id):
    return f'concept-{_id}'


def add_concepts(data, concepts):
    converted_pk = dict()
    current_pk = 0

    for concept in concepts:
        fields = concept['fields']
        old_pk = concept['pk']

        key_ = get_concept_key_(old_pk)

        name = fields['english_name']
        description = fields.get('description', None)
        concepticon_id = fields.get('concepticon_id', None)
        gld_id = fields.get('gld_id', None)

        add_kwargs = {
            'name': name,
            'id': slugify(name),
        }

        if concepticon_id is not None:
            add_kwargs['concepticon_id'] = concepticon_id

        if gld_id is not None:
            add_kwargs['gld_id'] = gld_id

        if description is not None:
            add_kwargs['description'] = description

        instance = data.add(models.Concept, key_, **add_kwargs)

        converted_pk[old_pk] = instance.pk
        current_pk += 1


def get_form_key_(_id):
    return f'form-{_id}'


def add_forms(data, forms):
    converted_pk = dict()
    current_pk = 0

    value_id_suffixes = defaultdict(int)

    for form in forms:
        fields = form['fields']
        old_pk = form['pk']

        key_ = get_form_key_(current_pk)

        name = fields['value']
        if not name:
            continue
        add_kwargs = {
            'name': name,
        }

        ipa = fields.get('ipa', None)
        if ipa is not None:
            add_kwargs['ipa'] = ipa

        markup_description = fields.get('markup_description', None)
        if markup_description is not None:
            add_kwargs['description'] = markup_description
            add_kwargs['markup_description'] = markup_description
            # add_kwargs['description'] = markup_description

        concept_old_pk = fields['concept']
        language_old_pk = fields['language']

        concept = data['Concept'][get_concept_key_(concept_old_pk)]
        language = data['Languoid'][get_languoid_key_(language_old_pk)]

        valueset_id = f'c{concept.id}-l{language.id}'
        value_id = f'{valueset_id}-{value_id_suffixes[valueset_id]}'
        value_id_suffixes[valueset_id] += 1
        add_kwargs['id'] = value_id

        if valueset_id in data['ValueSet']:
            vs = data['ValueSet'][valueset_id]
        else:
            vs = data.add(common.ValueSet, f'c{concept.id}-l{language.id}',
                          id=f'c{concept.id}-l{language.id}',
                          language=language,
                          parameter=concept,
                          )

        instance = data.add(models.Form, get_form_key_(old_pk), valueset=vs, **add_kwargs)

        converted_pk[old_pk] = instance.pk
        current_pk += 1


def main(args):
    data = Data()

    dataset = common.Dataset(id=moslex.__name__,
                             domain='moslex.clld.org', name='MosLex', license='https://creativecommons.org'
                                                                                     '/licenses/by-nc/4.0/',
                             jsondata={'license_icon': 'cc-by-nc.png', 'license_name': 'Creative Commons '
                                                                                       'Attribution-NC 4.0 '
                                                                                       'International License'})

    editor = data.add(common.Contributor, 'editor', id='editor', name='Alexei Kassian')
    common.Editor(dataset=dataset, contributor=editor)

    with open('languoids.json') as file:
        languoids = json.load(file)

    with open('concepts.json') as file:
        concepts = json.load(file)

    with open('forms.json') as file:
        forms = json.load(file)

    add_languoids(data, languoids)
    add_concepts(data, concepts)
    add_forms(data, forms)

    DBSession.add(dataset)

    # generic_contribution = common.Contribution(id='contrib', name='the contribution')


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodiucally whenever data has been updated.
    """


if __name__ == '__main__':  # pragma: no cover
    initializedb(create=main, prime_cache=prime_cache)
    sys.exit(0)
