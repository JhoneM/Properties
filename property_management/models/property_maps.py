from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    property_key_google_maps = fields.Char(string='Google Maps Api Key', config_parameter='property_maps.key')