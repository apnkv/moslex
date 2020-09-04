from clld.web.datatables.base import DataTable, Col, LinkCol, LinkToMapCol, IdCol, DetailsRowLinkCol
from clld.web.datatables.language import Languages
from clld.web.datatables.parameter import Parameters
from clld.web.datatables.value import Values, RefsCol, ValueSetCol, ValueNameCol
from clld.web.datatables.valueset import Valuesets

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.query import Query

from moslex import models

from clld.db.util import icontains
from clld.db.models.common import (
    Parameter, Language, Value, DomainElement, ValueSet, ValueSetReference
)
from clld.web.datatables.base import (
    LinkCol, DetailsRowLinkCol, LinkToMapCol, IntegerIdCol, filter_number, as_int
)


class StarlingLanguages(Languages):
    def col_defs(self):
        return [
            LinkCol(self, 'name'),
            Col(self,
                'glottocode_',
                sDescription='Glottolog code', model_col=models.Languoid.glottocode_),
            Col(self,
                'latitude',
                sDescription='<small>The geographic latitude</small>',
                model_col=models.Languoid.latitude, bSearchable=False),
            Col(self,
                'longitude',
                sDescription='<small>The geographic longitude</small>',
                model_col=models.Languoid.longitude, bSearchable=False),
            LinkToMapCol(self, 'm'),
        ]


class NumericCol(Col):
    def __init__(self, *args, **kwargs):
        super(NumericCol, self).__init__(*args, **kwargs)

    def search(self, qs):
        return filter_number(as_int(self.model_col), qs, type_=int)


class StarlingConcepts(Parameters):
    def col_defs(self):
        return [
            DetailsRowLinkCol(self, 'd'),
            LinkCol(self, 'name'),
            NumericCol(self, 'concepticon_id', sDescription='Concepticon ID', model_col=models.Concept.concepticon_id),
            NumericCol(self, 'gld_id', sDescription='GLD ID', model_col=models.Concept.gld_id)
        ]


class FormValueNameCol(ValueNameCol):

    def search(self, qs):
        if self.dt.parameter and self.dt.parameter.domain:
            return DomainElement.name.__eq__(qs)
        return icontains(models.Form.name, qs)


class StarlingForms(Values):
    def base_query(self, query: Query):
        query = query.join(ValueSet).options(
            joinedload(
                Value.valueset
            ).joinedload(
                ValueSet.references
            ).joinedload(
                ValueSetReference.source
            )
        )

        if self.language:
            query = query.join(ValueSet.parameter)
            if self.language.level == models.LanguoidLevel.group:
                children = self.language.children
                children_pks = [child.pk for child in children]
                filtered = query.filter(ValueSet.language_pk.in_(children_pks))
                filtered = filtered.join(ValueSet.language)
                return filtered

            return query.filter(ValueSet.language_pk == self.language.pk)

        if self.parameter:
            query = query.join(ValueSet.language)
            query = query.outerjoin(DomainElement).options(
                joinedload(Value.domainelement))
            return query.filter(ValueSet.parameter_pk == self.parameter.pk)

        if self.contribution:
            query = query.join(ValueSet.parameter)
            return query.filter(ValueSet.contribution_pk == self.contribution.pk)

        query = query.join(ValueSet.language).join(ValueSet.parameter)

        return query

    def col_defs(self):
        name_col = FormValueNameCol(self, 'value', model_col=models.Form.name)
        if self.parameter and self.parameter.domain:
            name_col.choices = [de.name for de in self.parameter.domain]

        res = [DetailsRowLinkCol(self, 'markup_description', model_col=models.Form.markup_description)]

        if self.parameter:
            return res + [
                LinkCol(self,
                        'language',
                        model_col=Language.name,
                        get_object=lambda i: i.valueset.language),
                name_col,
                Col(self, 'ipa', sTitle='IPA', model_col=models.Form.ipa),
                RefsCol(self, 'source'),
                LinkToMapCol(self, 'm', get_object=lambda i: i.valueset.language),
            ]

        if self.language:
            res += [
                LinkCol(self,
                        'parameter',
                        sTitle=self.req.translate('Parameter'),
                        model_col=Parameter.name,
                        get_object=lambda i: i.valueset.parameter),
            ]
            if self.language.level != models.LanguoidLevel.language:
                res += [
                    LinkCol(self,
                            'language',
                            model_col=Language.name,
                            get_object=lambda i: i.valueset.language)
                ]
            res += [
                name_col,
                Col(self, 'ipa', sTitle='IPA', model_col=models.Form.ipa),
                Col(self, 'cognate_class', sTitle='Cognate class', bSearchable=True, model_col=models.Form.cognate_class),
                # RefsCol(self, 'source'),
            ]
            return res

        return res + [
            LinkCol(self,
                    'parameter',
                    sTitle=self.req.translate('Parameter'),
                    model_col=models.Concept.name,
                    get_object=lambda i: i.valueset.parameter),
            name_col,
            LinkCol(self,
                    'language',
                    model_col=models.Languoid.name,
                    get_object=lambda i: i.valueset.language),
            Col(self, 'ipa', sTitle='IPA', model_col=models.Form.ipa),
            Col(self, 'cognate_class', sTitle='Cognate class', bSearchable=True, model_col=models.Form.cognate_class),
        ]


def includeme(config):
    config.register_datatable('languages', StarlingLanguages)
    config.register_datatable('parameters', StarlingConcepts)
    config.register_datatable('values', StarlingForms)
