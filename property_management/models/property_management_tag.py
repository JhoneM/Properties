# -*- coding: utf-8 -*-

from datetime import timedelta, date, datetime, time
from odoo import models, fields, api, exceptions, _

import logging
import pprint

_logger = logging.getLogger(__name__)

class PropertyManagementTag(models.Model):
    _description = "Características Propiedades"
    _name = 'property.management.tag'
    _inherit = ["mail.thread.cc", "mail.activity.mixin", "utm.mixin"]

    name = fields.Char(_('Nombre'), index=True, required=True)
    
    _sql_constraints = [('name_uniq', 'unique (name)', _("La Característica ingresada ya se encuentra registrada en el sistema."))]

    @api.model
    def fields_get(self, fields=None):
        fields_to_hide = ['activity_exception_decoration', 'campaign_id', 'email_cc', 'message_has_sms_error',
        					'message_has_error', 'source_id', 'medium_id', 'message_is_follower', 'message_follower_ids',
        					'message_channel_ids', 'message_partner_ids', 'activity_type_icon']
        res = super(PropertyManagementTag, self).fields_get()
        for field in fields_to_hide:
            res[field]['searchable'] = False
        return res
