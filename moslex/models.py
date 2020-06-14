from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Boolean,
    ForeignKey,
    UnicodeText,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin, DBSession
from clld.db.models import common
from clld.util import DeclEnum


class LanguoidLevel(DeclEnum):
    superfamily = 'superfamily', 'superfamily'
    family = 'family', 'family'
    group = 'group', 'group'
    language = 'language', 'language'


class TreeClosureTable(Base):
    __table_args__ = (UniqueConstraint('parent_pk', 'child_pk'),)
    parent_pk = Column(Integer, ForeignKey('languoid.pk'))
    child_pk = Column(Integer, ForeignKey('languoid.pk'))
    depth = Column(Integer)


@implementer(interfaces.ILanguage)
class Languoid(CustomModelMixin, common.Language):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)

    parent_pk = Column(Integer, ForeignKey('languoid.pk'))
    family_pk = Column(Integer, ForeignKey('languoid.pk'))

    descendants = relationship(
        'Languoid',
        order_by='Languoid.name, Languoid.id',
        foreign_keys=[family_pk],
        backref=backref('family', remote_side=[pk]))

    children = relationship(
        'Languoid',
        order_by='Languoid.name, Languoid.id',
        foreign_keys=[parent_pk],
        backref=backref('parent', remote_side=[pk]))

    glottocode_ = Column(Unicode(20))
    ethnologue_code = Column(Unicode(20))

    rich_description = Column(UnicodeText)
    nex_url = Column(String)
    description_file_url = Column(String)

    level = Column(LanguoidLevel.db_type())

    def get_identifier_objs(self, type_):
        if getattr(type_, 'value', type_) == common.IdentifierType.glottolog.value:
            return [
                common.Identifier(name=self.id, type=common.IdentifierType.glottolog.value)]
        return common.Language.get_identifier_objs(self, type_)

    def get_geocoords(self):
        """
        :return: sqlalchemy Query selecting quadrupels \
        (lid, primaryname, longitude, latitude) where lid is the Languoidbase.id of one\
        of the children of self.

        .. note::

            This method does not return the geo coordinates of the Languoid self, but of
            its descendants.
        """

        child_pks = DBSession.query(Languoid.pk) \
            .filter(Languoid.father_pk == self.pk).subquery()
        return DBSession.query(
            TreeClosureTable.parent_pk,
            common.Language.name,
            common.Language.longitude,
            common.Language.latitude,
            common.Language.id) \
            .filter(common.Language.pk == TreeClosureTable.child_pk) \
            .filter(TreeClosureTable.parent_pk.in_(child_pks)) \
            .filter(common.Language.latitude is not None)


@implementer(interfaces.IParameter)
class Concept(CustomModelMixin, common.Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)

    concepticon_id = Column(Integer, nullable=True)
    gld_id = Column(Integer, nullable=True)


@implementer(interfaces.IValue)
class Form(CustomModelMixin, common.Value):
    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)
    ipa = Column(Unicode(100))