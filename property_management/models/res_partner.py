# -*- coding: utf-8 -*-

from datetime import timedelta, date, datetime, time
from odoo import models, fields, api, exceptions, _

import logging
import pprint

_logger = logging.getLogger(__name__)

class PropertyManagementResPartner(models.Model):
    _inherit = 'res.partner'
    
    construction_company = fields.Boolean('Construction Company')

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_broker = fields.Boolean('Is Broker')