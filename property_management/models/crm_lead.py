# -*- coding: utf-8 -*-

from datetime import timedelta, date, datetime, time
from odoo import models, fields, api, exceptions, _

import logging
import pprint

_logger = logging.getLogger(__name__)

class PropertyManagementCrmLead(models.Model):
	_inherit = 'crm.lead'

	name = fields.Char(compute=False)

	crm_city_id = fields.Many2one(
		'res.city',
		string='City',
		domain="[('state_id', '=?', crm_state_id), ('country_id', '=?', crm_country_id)]",
		)
	crm_city = fields.Char(related='crm_city_id.name')
	crm_state_id = fields.Many2one("res.country.state", string='Región', ondelete='restrict', domain="[('country_id', '=?', crm_country_id)]")
	crm_zip = fields.Char(string=_("C.P."))
	crm_country_id = fields.Many2one('res.country', string='País', ondelete='restrict')
	
	@api.onchange('crm_city_id')
	def _onchange_crm_city_id(self):
		if self.crm_city_id.state_id:
			self.crm_state_id = self.crm_city_id.state_id
			self.crm_zip = self.crm_city_id.zipcode

	@api.onchange('crm_state_id')
	def _onchange_crm_state_id(self):
		if self.crm_state_id.country_id:
			self.crm_country_id = self.crm_state_id.country_id

		if self.crm_state_id and self.crm_state_id != self.crm_city_id.state_id:
			self.crm_city_id = False
			self.crm_zip = False

	@api.onchange('crm_country_id')
	def _onchange_crm_country_id(self):
		if self.crm_country_id and self.crm_country_id != self.crm_state_id.country_id:
			self.crm_city_id = False
			self.crm_state_id = False
			self.crm_zip = False

	@api.onchange('property_ids')
	def _onchange_calculate_active_propertys(self):
		current_propertys = []
		for rec in self.property_ids:
			current_propertys.append(rec.property_id.id)
		self.property_filter = [(6,0,current_propertys)]

	def _default_currency(self):
	    """
	    Carga la moneda por defecto
	    """
	    return self.env['res.currency'].search([('name', '=', 'CLP')], limit=1)
	
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
		search = []
		if self.bedroom_max != 0:
			search = search + [('bedroom_quantity', '>=', self.bedroom_min),('bedroom_quantity', '<=', self.bedroom_max)]
		if self.bathroom_max != 0:
			search = search + [('dependencies', '>=', self.bathroom_min),('dependencies', '<=', self.bathroom_max)]
		if self.total_area_max != 0:
			search = search + [('total_area', '>=', self.total_area_min),('total_area', '<=', self.total_area_max)]
		if self.real_estate_lease:
			search = search + [('real_estate_lease', '=', self.real_estate_lease)]
			if self.lease_price_max != 0 and self.lease_price_currency.name: 
				search = search + [('lease_price', '>=', self.lease_price_min),('lease_price', '<=', self.lease_price_max),('lease_price_currency.id', '=', self.lease_price_currency.id)]
		if self.real_estate_sale: 
			search = search + [('real_estate_sale', '=', self.real_estate_sale)]
			if self.sale_price_max != 0 and self.sale_price_currency.name: 
				search = search + [('sale_price', '>=', self.sale_price_min),('sale_price', '<=', self.sale_price_max),('sale_price_currency.id', '=', self.sale_price_currency.id)]
		if self.type_id:
			search = search + [('type_id.id','=',self.type_id.id)]
		if self.crm_city:
			search = search + [('city', '=', self.crm_city)]
		if self.crm_state_id.name:
			search = search + [('state_id.id', '=', self.crm_state_id.id)]
		if self.crm_zip:
			search = search + [('zip', '=', self.crm_zip)]
		if self.crm_country_id.name:
			search = search + [('country_id.id', '=', self.crm_country_id.id)]
		if len(self.characteristics.ids) > 0:
			for tag_id in self.characteristics.ids:
				search = search + [('tag_ids', 'in', tag_id)]
		if search:
			search = search + [('state_prop_id.code', '=', 4)]
			find_property = [] + self.env['property.management.property'].search(search).ids
			current = []
			for rec in self.property_ids:
				current.append(rec.property_id.id)
			for propertys in find_property:
				if propertys not in current:
					self.property_ids = [(0,0,{'property_id':propertys})]
			current_propertys = []
			for rec in self.property_ids:
				current_propertys.append(rec.property_id.id)
			self.property_filter = [(6,0,current_propertys)]

	property_filter = fields.Many2many('property.management.property')	
	property_ids = fields.One2many('crm.property.line','line_id')
	real_estate_lease = fields.Boolean('Arriendo')
	real_estate_sale = fields.Boolean('Compra')
	type_id = fields.Many2one('property.management.type', string=_('Tipo de Propiedad'), index=True, ondelete='cascade')
	requeriment_date = fields.Date('Fecha de Necesidad')
	real_estate_agent = fields.Many2one("hr.employee", string="Agente")
	referred_employee = fields.Many2one("hr.employee", string="Referido")
	sale_price = fields.Integer(string=_("Precio de Compra"))
	sale_price_currency = fields.Many2one('res.currency', string=_("Moneda de Compra"), domain=_get_currency, default=_default_currency)
	lease_price = fields.Integer(string=_("Precio de Arriendo"))
	lease_price_currency = fields.Many2one('res.currency', string=_("Moneda de Arriendo"), domain=_get_currency, default=_default_currency)
	bedroom_min = fields.Integer('Mín. Dormitorios')
	bedroom_max = fields.Integer('Máx. Dormitorios')
	bathroom_min = fields.Integer('Mín. Baños')
	bathroom_max = fields.Integer('Máx. Baños')
	total_area_min = fields.Integer('Mín. Superficie Total')
	total_area_max = fields.Integer('Máx. Superficie Total')
	sale_price_min = fields.Integer('Mín. Precio de Compra')
	sale_price_max = fields.Integer('Máx. Precio de Compra')
	lease_price_min = fields.Integer('Mín. Precio de Arriendo')
	lease_price_max = fields.Integer('Máx. Precio de Arriendo')
	characteristics = fields.Many2many('property.management.tag', string=_("Características"))

class CRMPropertyLine(models.Model):
	_name = 'crm.property.line'
	_inherit = ["mail.thread.cc", "mail.activity.mixin", "utm.mixin", "image.mixin"]
	
	@api.onchange('property_id')
	def onchange_property_id_filter(self):
		available = []
		find_property_ids = self.env['property.management.property'].search([])
		for rec in find_property_ids:
			if rec.state_prop_id.code == '4':
				available.append(rec.id)

		res = {'domain' : {'property_id' : ['&',('id', 'not in', self.property_filter.ids),('id', 'in', available)]}}
		return res

	@api.onchange('property_id')
	def compute_display_attributes(self):
	    """
	    Formatea el valor de 'attributes'
	    """
	    for rec in self.property_id:
	        self.attributes ="<span class='fa fa-bed'>{}</span><br><span class='fa fa-bath'>{}</span><br><span class='fa fa-arrows-alt'>{}</span>".format(rec.bedroom_quantity, rec.dependencies, rec.total_area)

	@api.onchange('property_id')
	def compute_display_price(self):
		"""
		Formatea el valor de 'price'
		"""
		for rec in self.property_id:
			if self.line_id.real_estate_sale:
				if rec.sale_price_currency.name:
					self.price ="<p>{}<br>{}</p>".format(rec.sale_price, rec.sale_price_currency.name)
				else:
					self.price ="<p>{}<br>".format(rec.sale_price)
			else:
				self.price ="<p>{}<br>{}</p>".format(rec.lease_price, rec.lease_price_currency.name)
 
	@api.onchange('property_id')
	def compute_display_address(self):
	    """
	    Formatea el valor de 'address'
	    """
	    for rec in self.property_id:
	        address ="<p>"
	        if rec.street:
	            address = address + rec.street + "<br>" 
	        if rec.street2:
	            address = address + rec.street2 + "<br>"
	        if rec.zip:
	            address = address + rec.zip + "<br>"
	        if rec.city:
	            address = address + rec.city + "<br>"
	        if rec.state_id.name:
	            address = address + rec.state_id.name + "<br>"
	        if rec.country_id.name:
	            address = address +rec.country_id.name + "<br>"
	        self.address = address + "<p>"

	property_filter = fields.Many2many('property.management.property', related='line_id.property_filter')	
	line_id = fields.Many2one ('crm.lead')
	property_id = fields.Many2one('property.management.property', string=_('Propiedades'), required=True)
	image_1920 = fields.Binary("Imagen", store=True, related='property_id.image_1920')
	evaluation = fields.Selection([('0', 'Cero'), ('1', 'Primero'), ('2', 'Segundo'),('3', 'Tercero')])
	visits = fields.Boolean(string="Visitas", store=True)
	visits_date = fields.Date(string="Fecha de Visitas")
	previous_evaluation = fields.Selection([('0', 'Cero'), ('1', 'Primero'), ('2', 'Segundo'),('3', 'Tercero')])
	visits_order = fields.Binary("Orden de Visita")
	address = fields.Html(string="Dirección", store=True, related='property_id.address', force_save="1")
	price = fields.Html(string="Precio", related='property_id.price', store=True, force_save="1")
	attributes = fields.Html(string="Atributos", related='property_id.attributes', store=True, force_save="1")
