# -*- coding: utf-8 -*-

from datetime import timedelta, date, datetime, time
from odoo import models, fields, api, exceptions, _

import logging
import pprint

_logger = logging.getLogger(__name__)

class PropertyManagementCrmLead(models.Model):
	_inherit = 'crm.lead'

	@api.model
	def _filter_property_ids(self):
		"""
		Filtra las propiedades que esten en estado "Captación"
		"""
		available = []
		find_property_ids = self.env['property.management.property'].search([])

		for rec in find_property_ids:
			if rec.state_prop_id.code == '4':
				available.append(rec.id)

		return [('id', 'in', available)]

	def _default_currency(self):
	    """
	    Carga la moneda por defecto
	    """
	    return self.env['res.currency'].search([('name', '=', 'CLP')], limit=1)

	@api.onchange('property_ids.evaluation')
	def _onchange_evaluation(self):
		for rec in self.property_ids:
			if rec.pivot_evaluation != rec.evaluation: 
				rec.previous_evaluation = rec.pivot_evaluation
				rec.pivot_evaluation = rec.evaluation    
	
	@api.model
	def _get_currency(self):
	    """
	    Filtra las monedas a mostrar
	    """
	    find_currency = self.env['res.currency'].search([
	        ('name', 'in', ['USD', 'CLP', 'UF'])
	    ])
	
	    currency_ids =  [rec.id for rec in find_currency]
	    return [('id', 'in', currency_ids)]

	def search_propertys (self):
		search = [('state_prop_id.code', '=', 4)]
		if self.bedroom_max != 0:
			search = search + [('bedroom_quantity', '>=', self.bedroom_min),('bedroom_quantity', '<=', self.bedroom_max)]
		if self.bathroom_max != 0:
			search = search + [('dependencies', '>=', self.bathroom_min),('dependencies', '<=', self.bathroom_max)]
		if self.total_area_max != 0:
			search = search + [('total_area', '>=', self.total_area_min),('total_area', '<=', self.total_area_max)]
		if self.real_estate_lease and self.lease_price_max != 0 and self.lease_price_currency.name: 
			search = search + [('lease_price', '>=', self.lease_price_min),('lease_price', '<=', self.lease_price_max),('lease_price_currency.id', '=', self.lease_price_currency.id)]
		if self.real_estate_sale and self.sale_price_max != 0 and self.sale_price_currency.name: 
			search = search + [('sale_price', '>=', self.sale_price_min),('sale_price', '<=', self.sale_price_max),('sale_price_currency.id', '=', self.sale_price_currency.id)]
		if self.type_id:
			search = search + [('type_id.id','=',self.type_id.id)]
		if self.city:
			search = search + [('city', '=', self.city)]
		if self.state_id.name:
			search = search + [('state_id.id', '=', self.state_id.id)]
		if self.zip:
			search = search + [('zip', '=', self.zip)]
		if self.country_id.name:
			search = search + [('country_id.id', '=', self.country_id.id)]
		if len(self.characteristics.ids) > 0:
			for tag_id in self.characteristics.ids:
				search = search + [('tag_ids', 'in', tag_id)]
		find_property = [] + self.env['property.management.property'].search(search).ids
		self.property_ids = [(6,0,find_property)]

	property_ids = fields.Many2many('property.management.property', string=_('Propiedades'), domain=_filter_property_ids, required=True)
	real_estate_lease = fields.Boolean('Arriendo')
	real_estate_sale = fields.Boolean('Venta')
	type_id = fields.Many2one('property.management.type', string=_('Tipo'), index=True, ondelete='cascade')
	requeriment_date = fields.Date('Fecha de Necesidad')
	real_estate_agent = fields.Many2one("hr.employee", string="Agente")
	referred_employee = fields.Many2one("hr.employee", string="Referido")
	sale_price = fields.Float(string=_("Precio de venta"), digits=(16, 3))
	sale_price_currency = fields.Many2one('res.currency', string=_("Moneda"), domain=_get_currency, default=_default_currency)
	lease_price = fields.Float(string=_("Precio de arriendo"), digits=(16, 3))
	lease_price_currency = fields.Many2one('res.currency', string=_("Moneda"), domain=_get_currency, default=_default_currency)
	bedroom_min = fields.Integer('Min dormitorios')
	bedroom_max = fields.Integer('Max dormitorios')
	bathroom_min = fields.Integer('Min baños')
	bathroom_max = fields.Integer('Max baños')
	total_area_min = fields.Integer('Min superficie total')
	total_area_max = fields.Integer('Max superficie total')
	sale_price_min = fields.Integer('Min precio de venta')
	sale_price_max = fields.Integer('Max precio de venta')
	lease_price_min = fields.Integer('Min precio de arriendo')
	lease_price_max = fields.Integer('Max precio de arriendo')
	characteristics = fields.Many2many('property.management.tag', string=_("Características"))