from sqlalchemy.orm import joinedload
from clld.web import datatables
from clld.web.datatables.base import LinkCol, Col, LinkToMapCol


from moslex import models





def includeme(config):
    """register custom datatables"""
