# -*- coding: utf-8 -*-

from datetime import timedelta, date, datetime, time
from odoo import models, fields, api, exceptions, _

import logging
import pprint

_logger = logging.getLogger(__name__)

class PropertyManagementType(models.Model):
    _description = "Tipo de Propiedad"
    _name = 'property.management.type'
    _inherit = ["mail.thread.cc", "mail.activity.mixin", "utm.mixin"]

    name = fields.Char(_('Nombre'), index=True, required=True)
    
    _sql_constraints = [('name_uniq', 'unique (name)', _("Tipo already exists !"))]

    