# -*- coding: utf-8 -*-

from datetime import timedelta, date, datetime, time
from odoo import models, fields, api, exceptions, _

import logging
import pprint

_logger = logging.getLogger(__name__)

class PropertyManagementOrientation(models.Model):
    _description = "Orientación Propiedades"
    _name = 'property.management.orientation'
    _inherit = ["mail.thread.cc", "mail.activity.mixin", "utm.mixin"]

    name = fields.Char(_('Nombre'), index=True, required=True)
    
    _sql_constraints = [('name_uniq', 'unique (name)', _("Nombre ya existe !"))]

    