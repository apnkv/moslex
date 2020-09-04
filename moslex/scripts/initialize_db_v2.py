import glob
import json
import os
import math
from collections import defaultdict

from clld.scripts.util import Data, initializedb
from clld.db.meta import DBSession
from clld.db.models import common
from slugify import slugify

import moslex
from moslex import models
from gld2json.parsers import parse_gld_xls


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodiucally whenever data has been updated.
    """


def add_concepts(data, concepts):
    for concept in concepts:
        fields = concept['fields']

        key_ = f'{concept["fields"]["gld_id"]}'

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

        data.add(models.Concept, key_, **add_kwargs)


def get_languoid_key_(_id):
    return f'languoid-{_id}'


def add_languoids(data, languoids: dict):
    instances = []
    id_to_instance = dict()

    for slug, fields in languoids.items():
        key_ = slug

        name = fields['name']
        parent = fields.get('parent', None)
        latitude = fields.get('lat', None)
        longitude = fields.get('lng', None)
        rich_description = fields.get('rich_description', None)
        glottocode = fields.get('glottolog', None)
        ethnologue_code = fields.get('ethnologue', None)
        nex_url = fields.get('nex_url', None)
        description_file_url = fields.get('description_file_url', None)

        add_kwargs = {
            'name': name,
            'id': key_,
        }

        if parent is not None:
            add_kwargs['parent'] = id_to_instance[parent]

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

        add_kwargs['level'] = fields.get('level', models.LanguoidLevel.language)

        instance = data.add(models.Languoid, key_, **add_kwargs)
        instances.append(instance)
        id_to_instance[instance.id] = instance

        if glottocode is not None:
            identifier = data.add(models.Identifier, f'{key_}-glottocode',
                                  type=models.IdentifierType.glottolog.value,
                                  name=glottocode)
            DBSession.add(common.LanguageIdentifier(language=instance, identifier=identifier))

        if ethnologue_code is not None:
            identifier = data.add(models.Identifier, f'{key_}-ethnologue',
                                  type=models.IdentifierType.ethnologue.value,
                                  name=ethnologue_code)
            DBSession.add(common.LanguageIdentifier(language=instance, identifier=identifier))

    return instances


def add_forms(data, forms):
    instances = []

    value_id_suffixes = defaultdict(int)

    for form in forms:
        name = form['form']
        if not name or (type(name) != str and math.isnan(name)):
            continue
        add_kwargs = {
            'name': name,
        }

        ipa = form.get('ipa', None)
        if ipa is not None:
            add_kwargs['ipa'] = ipa

        cognate_class = form.get('cognate_class', None)
        if cognate_class is not None:
            add_kwargs['cognate_class'] = cognate_class

        comment = form.get('comment', None)
        if comment is not None:
            add_kwargs['description'] = comment
            add_kwargs['markup_description'] = comment
            # add_kwargs['description'] = markup_description

        concept = data['Concept'][f'{form["gld_word_id"]}']
        language = data['Languoid'][f'{form["language"]}']

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

        instance = data.add(models.Form, value_id, valueset=vs, **add_kwargs)
        instances.append(instance)

    return instances


def add_data_folder(path, data):
    meta_path = os.path.join(path, 'meta.json')
    with open(meta_path, 'r') as file:
        meta = json.load(file)

    meta_languoids = add_languoids(data, meta['languoids'])
    group = None
    n_groups = 0
    for languoid in meta_languoids:
        if languoid.level == models.LanguoidLevel.group.value:
            group = languoid
            group.level = models.LanguoidLevel.group
            n_groups += 1

    if group is None:
        raise ValueError(f'Meta file {meta_path} contains no group information')

    if n_groups > 1:
        raise ValueError(f'Data folder {path} has an ambiguous group, please check meta.json')

    gld = parse_gld_xls(os.path.join(path, meta['xls_file']))
    languages = add_languoids(data, gld['languages'])
    for language in languages:
        language.parent = group

    add_forms(data, gld['forms'])


def main(args):
    data = Data()

    dataset = common.Dataset(id=moslex.__name__,
                             domain='moslex.clld.org', name='MosLex', license='https://creativecommons.org'
                                                                              '/licenses/by-nc/4.0/',
                             jsondata={'license_icon': 'cc-by-nc.png', 'license_name': 'Creative Commons '
                                                                                       'Attribution-NC 4.0 '
                                                                                       'International License'})

    editor = data.add(common.Contributor, 'editor', id='editor', name='Alexei Kassian',
                      email='alexei.kassian@gmail.com')
    common.Editor(dataset=dataset, contributor=editor)

    with open(os.environ['MOSLEX_CONCEPTS']) as file:
        concepts = json.load(file)
    add_concepts(data, concepts)

    data_folders = [path for path in glob.glob(os.path.join(os.environ['MOSLEX_DATA'], '*')) if os.path.isdir(path)]
    for folder in data_folders:
        add_data_folder(folder, data)

    DBSession.add(dataset)


if __name__ == '__main__':  # pragma: no cover
    initializedb(create=main, prime_cache=prime_cache)
