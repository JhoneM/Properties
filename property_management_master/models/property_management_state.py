# -*- coding: utf-8 -*-

from datetime import timedelta, date, datetime, time
from odoo import models, fields, api, exceptions, _

import logging
import pprint

_logger = logging.getLogger(__name__)

class PropertyManagementState(models.Model):
    _name = 'property.management.state'
    _inherit = ["crm.stage", "mail.thread.cc", "mail.activity.mixin", "utm.mixin"]
    
    code = fields.Char(_('Código'))
