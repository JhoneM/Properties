# -*- coding: utf-8 -*-

from datetime import timedelta, date, datetime, time
from odoo import models, fields, api, exceptions, _

import logging
import pprint

_logger = logging.getLogger(__name__)

class PropertyManagementOrigin(models.Model):
    _description = "Orígenes de las Propiedades"
    _name = 'property.management.origin'
    _inherit = ["mail.thread.cc", "mail.activity.mixin", "utm.mixin"]

    name = fields.Char(_('Nombre'), index=True, required=True)
    no_editable = fields.Boolean('Campo No Editable')
    
    _sql_constraints = [('name_uniq', 'unique (name)', _("El Origen ingresado ya se encuentra registrado en el sistema."))]
    
    @api.onchange('name')
    def _onchange_name(self):
        if self.no_editable:
            raise exceptions.ValidationError(_("No puede modificar este registro."))

    def unlink(self):
        for rec in self:
            if rec.no_editable:
                raise exceptions.ValidationError(_("No puede eliminar este registro."))
        return super(PropertyManagementOrigin, self).unlink()

    @api.model
    def fields_get(self, fields=None):
        fields_to_hide = ['no_editable', 'activity_exception_decoration', 'campaign_id',
                            'email_cc', 'message_has_sms_error', 'message_has_error', 'source_id', 'medium_id',
                            'message_is_follower', 'message_follower_ids', 'message_channel_ids', 'message_partner_ids',
                            'activity_type_icon']
        res = super(PropertyManagementOrigin, self).fields_get()
        for field in fields_to_hide:
            res[field]['searchable'] = False
        return res
