# -*- coding: utf-8 -*-

from datetime import timedelta, date, datetime, time
from odoo import models, fields, api, exceptions, _

import logging
import pprint

_logger = logging.getLogger(__name__)

class PropertyManagementPropertyImage(models.Model):
    _description = "Imagen de Propiedad"
    _name = 'property.management.property.image'
    _order = 'orden asc'

    property_parent_id = fields.Many2one('property.management.property')
    name = fields.Char(_('Nombre'), index=True, required=True)
    image = fields.Image("Imagen", max_width=1920, max_height=1920, store=True)
    orden = fields.Integer('Orden')

    
