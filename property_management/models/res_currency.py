from odoo import models, api

import logging

_logger = logging.getLogger(__name__)


class resCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        currency_ids = res.mapped('currency_id')

        property_ids = self.env['property.management.property'].search(
                ['|', ('sale_price_currency', 'in', currency_ids.ids), ('lease_price_currency', 'in', currency_ids.ids)])
        property_ids._compute_price_company_currency()

        return res

    def write(self, vals):
        res = super().write(vals)
        if 'rate' in vals:
            currency_ids = self.mapped('currency_id')
            property_ids = self.env['property.management.property'].search(
                ['|', ('sale_price_currency', 'in', currency_ids.ids), ('lease_price_currency', 'in', currency_ids.ids)])
            property_ids._compute_price_company_currency()

        return res
