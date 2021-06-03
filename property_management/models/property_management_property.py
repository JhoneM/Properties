# -*- coding: utf-8 -*-

from datetime import timedelta, date, datetime, time
from odoo import models, fields, api, exceptions, _

import json
import requests
import logging
import pprint

_logger = logging.getLogger(__name__)

URL_API_MAPS = '<img id="map" src="https://maps.googleapis.com/maps/api/staticmap?zoom={}&size=400x400&markers=color:red%7Clabel:P%7C{}&key={}"/>'

class PropertyManagementProperty(models.Model):
    _description = "Propiedad"
    _name = 'property.management.property'
    _inherit = ["mail.thread.cc", "mail.activity.mixin", "utm.mixin", "image.mixin", "website.seo.metadata","website.published.mixin"]

    name = fields.Char(_('Nombre'), index=True)
    
    @api.model
    def _read_group_stage_ids(self,stages,domain,order):
        """
        Ordena los estados de las propiedades
        """
        state_ids = self.env['property.management.state'].search([])
        return state_ids
    
    def _get_default_state_prop_id(self):
        """
        Carga el estado Identificación por defecto
        """
        state = self.env['property.management.state'].search([
            ('code', '=', '1')
        ], limit=1)
        return state.id if state else None

    @api.depends("property_coordenada")
    def _compute_lat_lng(self):
        for record in self:
            if record.property_coordenada:
                lat_lng = record.property_coordenada.split()

                if len(lat_lng) == 2:
                    record.property_coordenada_lat = lat_lng[0]
                    record.property_coordenada_lng = lat_lng[1]
                else:
                    record.property_coordenada_lat = ""
                    record.property_coordenada_lng = ""
            else:
                record.property_coordenada_lat = ""
                record.property_coordenada_lng = ""

    @api.depends('name', 'street', 'street2', 'city_id', 'state_id', 'country_id')
    def _compute_address(self):
        for record in self:
            address_format = "%(name)s\n %(street)s\n%(street2)s\n%(city)s\n%(state_name)s\n%(country_name)s"
            args = {
                'street': record.street,
                'street2': record.street2,
                'state_code': record.state_id.code or '',
                'state_name': record.state_id.name or '',
                'city': record.city_id.name or '',
                'country_code': record.country_id.code or '',
                'zip': record.zip or '',
                'country_name': record.country_id.display_name,
                'name': record.name,
            }
            record.address_text = address_format % args

    def format_int_price(self, num):
        return f"{num:,}".format(num).replace(",", ".")

    state_prop_id = fields.Many2one('property.management.state', group_expand='_read_group_stage_ids', string=_('Estado'), default=_get_default_state_prop_id)
    type_id = fields.Many2one('property.management.type', string=_('Tipo de Propiedad'), index=True, ondelete='cascade')
    total_area = fields.Integer(string=_("Superficie Total"))
    builded_surface = fields.Integer(string=_("Superficie Construida"))
    partner_id = fields.Many2one('res.partner', string=_("Contacto"), index=True)
    cons_year = fields.Char(string=_("Año de Construcción"))
    num_rol = fields.Char(string=_("Número de Rol"))
    street = fields.Char(string=_("Calle"))
    street2 = fields.Char(string=_("Calle 2"))
    zip = fields.Char(string=_("C.P."))
    state_id = fields.Many2one("res.country.state", string='Región', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='País', ondelete='restrict')
    amb_ids = fields.Many2many('property.management.amb', string=_("Espacios"))
    bedroom_quantity = fields.Integer(string=_("Dormitorios"))
    dependencies = fields.Integer(string=_("Baños"))
    cellar = fields.Integer(string=_("Bodegas"))
    parking = fields.Integer(string=_("Estacionamientos"))
    orientation_id = fields.Many2one('property.management.orientation', string=_('Orientación'), index=True, ondelete='cascade')
    tag_ids = fields.Many2many('property.management.tag', string=_("Características"))
    community_name = fields.Char(string=_("Nombre de Comunidad"))
    construction_company_id = fields.Many2one('res.partner', string=_("Constructora"), index=True,)
    floor_quantity = fields.Integer(string=_("Cantidad de Pisos"))
    dep_x_floor = fields.Integer(string=_("Departamentos por Piso"))
    num_floor= fields.Char(string=_("Piso"))
    elevator = fields.Integer(string=_("Ascensores"))
    image_ids = fields.One2many('property.management.property.image', 'property_parent_id', 'Imágenes de la Propiedad')
    expiration_date = fields.Date('Fecha de Vencimiento')
    origin = fields.Selection([('external','Externa'),('employee','Empleado')])
    origin_property = fields.Many2one('property.management.origin', 'Origen')
    origin_name = fields.Char('Origin', compute='_compute_origin_name', store=True)
    broker = fields.Many2one('res.partner', 'Corredora', domain=[("is_broker", "=", "True")])
    employee = fields.Many2one('hr.employee', 'Empleado')
    key = fields.Boolean('Llaves')
    head = fields.Char('Encabezado')
    description = fields.Text('Descripción')
    attachments = fields.One2many('property.attachments','property_id', string='Documentos Adjuntos')
    
    property_maps = fields.Html('Image Html', store=True )
    property_coordenada = fields.Char("Coordenadas")
    property_coordenada_lat = fields.Char("Coordenada Lat", compute="_compute_lat_lng", store=True)
    property_coordenada_lng = fields.Char("Coordenadas Lng", compute="_compute_lat_lng", store=True)


    zoom = fields.Selection(selection=[('10', '10'), ('11', '11'),('12', '12'),
                                       ('13', '13'), ('14', '14'),('15', '15'),
                                       ('16', '16'), ('17', '17'),('18', '18'),
                                       ('19', '19'), ('20', '20')], string="Zoom", default="15")
    
    city_id = fields.Many2one(
        'res.city',
        string='City',
        domain="[('state_id', '=?', state_id), ('country_id', '=?', country_id)]",
    )
    city = fields.Char(related='city_id.name')

    @api.onchange('city_id')
    def _onchange_city_id(self):
        if self.city_id.state_id:
            self.state_id = self.city_id.state_id
            self.zip = self.city_id.zipcode

    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

        if self.state_id and self.state_id != self.city_id.state_id:
            self.city_id = False
            self.zip = False

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.city_id = False
            self.state_id = False
            self.zip = False
    
    @api.onchange('origin_property')
    def _onchange_origin_property(self):
            self.employee = False
            self.broker = False

    @api.depends('street', 'zip', 'city', 'country_id')
    def _compute_complete_address(self):
        for record in self:
            record.contact_address_complete = ''
            if record.street:
                record.contact_address_complete += record.street + ', '
            if record.zip:
                record.contact_address_complete += record.zip + ' '
            if record.city:
                record.contact_address_complete += record.city + ', '
            if record.country_id:
                record.contact_address_complete += record.country_id.name
            record.contact_address_complete = record.contact_address_complete.strip().strip(',')

    @api.depends('origin_property')
    def _compute_origin_name(self):
        for rec in self:
            rec.origin_name = rec.origin_property.name

    @api.onchange('property_coordenada')
    def _onchange_property_coordenada(self):
        key = self.env['ir.config_parameter'].sudo().get_param('property_maps.key')
        self.property_maps = URL_API_MAPS.format(str(self.zoom), str(self.property_coordenada), str(key))

    @api.onchange('zoom')
    def _onchange_zoom(self):
        key = self.env['ir.config_parameter'].sudo().get_param('property_maps.key')
        self.property_maps = URL_API_MAPS.format(str(self.zoom), str(self.property_coordenada), str(key))
    
    @api.onchange('street','street2','state_id','city','zip','country_id')
    def _onchange_address(self):
        address = ""
        key = self.env['ir.config_parameter'].sudo().get_param('property_maps.key')
        for rec in self:
            if rec.street:
                address += str(rec.street) + "+"
            if rec.street2:
                address += str(rec.street2) + "+"
            if rec.state_id:
                address += str(rec.state_id.name) + "+"
            if rec.city:
                address += str(rec.city) + "+"
            if rec.zip:
                address += str(rec.zip) + "+"
            if rec.country_id:
                address += str(rec.country_id.name) + "+"
        r = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address=" + address + "&key=" + str(key))   
        dic = json.loads(r.text)
        if str(dic["status"]) == "OK":
            self.property_coordenada = str(dic["results"][0]["geometry"]["location"]["lat"]) + " " + str(dic["results"][0]["geometry"]["location"]["lng"])


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
    
    @api.depends('total_area', 'bedroom_quantity','dependencies')
    def compute_display_attributes(self):
        """
        Formatea el valor de 'attributes'
        """
        for rec in self:
            rec.attributes ="<span class='fa fa-bed'>{}</span><br><span class='fa fa-bath'>{}</span><br><span class='fa fa-arrows-alt'>{}</span>".format(rec.bedroom_quantity, rec.dependencies, rec.total_area)

    @api.depends('visiting_hours')
    def compute_visits(self):
        """
        Formatea el valor de 'visits'
        """
        for rec in self:
            visits = False
            if rec.visiting_hours:
                visits = True
            rec.visits = visits 
    

    @api.depends('sale_price', 'sale_price_currency','lease_price', 'lease_price_currency','real_estate_sale', 'real_estate_lease')
    def compute_display_price(self):
        """
        Formatea el valor de 'price'
        """
        for rec in self:
            if rec.real_estate_sale:
                rec.price ="<p>{}<br>{}</p>".format(rec.sale_price, rec.sale_price_currency.name)
            else:    
                rec.price ="<p>{}<br>{}</p>".format(rec.lease_price, rec.lease_price_currency.name)
        

    @api.depends('street','street2','zip','city','state_id','country_id')
    def compute_display_address(self):
        """
        Formatea el valor de 'address'
        """
        for rec in self:
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
            rec.address = address + "<p>"

    
    sale_price_company_currency = fields.Float(
        string=_("Precio de venta en monena de la compania"),
        digits=(16, 3),
        compute='_compute_price_company_currency',
        store=True
    )

    lease_price_company_currency = fields.Float(
        string=_("Precio de arriendo en monena de la compania"),
        digits=(16, 3),
        compute='_compute_price_company_currency',
        store=True
    )
    
    address_text = fields.Text(
        string='address',
        compute='_compute_address',
        store=True,
    )

    sale_price = fields.Integer(string=_("Precio de Venta"))
    sale_price_currency = fields.Many2one('res.currency', string=_("Moneda de Venta"), domain=_get_currency, default=_default_currency)
    lease_price = fields.Integer(string=_("Precio de Arriendo"))
    lease_price_currency = fields.Many2one('res.currency', string=_("Moneda de Arriendo"), domain=_get_currency, default=_default_currency)
    tax_assessment = fields.Float(string=_("Tasación Fiscal"), digits=(16, 3))
    tax_assessment_currency = fields.Many2one('res.currency', default=_default_currency)
    commercial_appraisal = fields.Float(string=_("Tasación Comercial"), digits=(16, 3))
    commercial_appraisal_currency = fields.Many2one('res.currency', domain=_get_currency, default=_default_currency)
    common_expenses = fields.Float(string=_("Gastos Comunes"), digits=(16, 3))
    common_expenses_currency = fields.Many2one('res.currency', domain=_get_currency, default=_default_currency)
    contributions = fields.Float(string=_("Contribuciones"), digits=(16, 3))
    contributions_currency = fields.Many2one('res.currency', domain=_get_currency, default=_default_currency)
    exclusiveness = fields.Boolean(string=_("Exclusividad"))
    external_property = fields.Boolean(string=_("Origen Externo"))
    visiting_hours = fields.Char(string=_("Horario de Visita"))
    sign = fields.Boolean(string=_("Letrero"))
    compute_price_lease = fields.Char(string=_("Comisión Arriendo"))
    compute_price_fixed = fields.Boolean("Precio Fijo (Comisión Arriendo)")
    agreed_commission_fixed = fields.Float(digits=(16, 3), string=_("Valor del Precio Fijo (Comisión Arriendo)"))
    agreed_commission_currency = fields.Many2one('res.currency', string=_("Moneda (Comisión Arriendo)"), domain=_get_currency, default=_default_currency)
    compute_price_percentage = fields.Boolean("Porcentaje (Comisión Arriendo)")
    agreed_commission_percent = fields.Float(digits=(16, 3), string=_("Valor del Porcentaje (Comisión Arriendo)"))
    compute_price_sale = fields.Char(string=_("Comisión Venta"))
    compute_price_fixed_sale = fields.Boolean("Precio Fijo (Comisión Venta)")
    agreed_commission_fixed_sale = fields.Float(digits=(16, 3), string=_("Valor del Precio Fijo (Comisión Venta)"))
    agreed_commission_currency_sale = fields.Many2one('res.currency', string=_("Moneda (Comisión Venta)"), domain=_get_currency, default=_default_currency)
    compute_price_percentage_sale = fields.Boolean("Porcentaje (Comisión Venta)")
    agreed_commission_percent_sale = fields.Float(digits=(16, 3), string=_("Valor del Porcentaje (Comisión Venta)"))
    virtual_tour = fields.Char(string=_("Tour Virtual"))
    video = fields.Char(string=_("Video"))
    # partner_latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    # partner_longitude = fields.Float(string='Geo Longitude', digits=(16, 5))   
    amenities = fields.Many2many("property.amenities", string="Amenities")
    restrictions = fields.Many2many("property.restrictions", string="Restricciones")
    real_estate_lease = fields.Boolean("Arriendo")
    real_estate_sale = fields.Boolean("Venta")
    real_estate_agent = fields.Many2one("hr.employee", string="Agente")
    address = fields.Html(string="Dirección", store=True, compute='compute_display_address')
    price = fields.Html(string="Precio", compute='compute_display_price', store=True)
    attributes = fields.Html(string="Atributos", compute='compute_display_attributes', store=True)
    evaluation = fields.Selection([('0', 'Cero'), ('1', 'Primero'), ('2', 'Segundo'),('3', 'Tercero')])
    visits = fields.Boolean(string="Visitas", compute='compute_visits', store=True)
    visits_date = fields.Date(string="Fecha de Visitas")
    previous_evaluation = fields.Selection([('0', 'Cero'), ('1', 'Primero'), ('2', 'Segundo'),('3', 'Tercero')])
    visits_order = fields.Binary("Orden de Visita")
    team_id = fields.Many2one("crm.team", string="Sucursal")

    pivot_evaluation = fields.Selection(
        [('0', 'Cero'),
         ('1', 'Primero'),
         ('2', 'Segundo'),
         ('3', 'Tercero')]
    )
    visits_order = fields.Binary("Orden de visita")

    seo_name = fields.Char(
        string='seo name',
        compute='compute_seo_name'
    )

    @api.depends('head')
    def compute_seo_name(self):
        for record in self:
            record.seo_name = record.head

    def _compute_website_url(self):
        for record in self:
            record.website_url = "/propiedad/%s" % (record.id)

    @api.onchange('evaluation')
    def _onchange_evaluation(self):
        for rec in self:
            rec.previous_evaluation = rec.pivot_evaluation
            rec.pivot_evaluation = rec.evaluation

    @api.model
    def cron_compute_price_company_currency(self):
        self.search([])._compute_price_company_currency()
        self.search([])._compute_address()

    @api.depends('state_id', 'sale_price', 'sale_price_currency', 'lease_price', 'lease_price_currency')
    def _compute_price_company_currency(self):
        company_currency_id = self.env['res.company']._company_default_get().currency_id
        for record in self:
            if record.sale_price_currency.id == company_currency_id.id:
                record.sale_price_company_currency = record.sale_price
                record.lease_price_company_currency = record.lease_price
            else:
                record.sale_price_company_currency = record.sale_price_currency._convert(
                    record.sale_price,
                    company_currency_id,
                    self.env.company,
                    fields.Date.today()
                )
                record.lease_price_company_currency = record.lease_price_currency._convert(
                    record.lease_price,
                    company_currency_id,
                    self.env.company,
                    fields.Date.today()
                )


    @api.onchange('compute_price_fixed')
    def _onchange_compute_price_fixed(self):
            self.agreed_commission_fixed = False
            self.agreed_commission_currency = 45

    @api.onchange('compute_price_percentage')
    def _onchange_compute_price_percentage(self):
            self.agreed_commission_percent = False

    @api.onchange('compute_price_fixed_sale')
    def _onchange_compute_price_fixed_sale(self):
            self.agreed_commission_fixed_sale = False
            self.agreed_commission_currency_sale = 45

    @api.onchange('compute_price_percentage_sale')
    def _onchange_compute_price_percentage_sale(self):
            self.agreed_commission_percent_sale = False

    @api.onchange('real_estate_lease')
    def _onchange_real_estate_lease(self):
            self.lease_price = False
            self.lease_price_currency = 45
            self.compute_price_fixed = False
            self.compute_price_percentage = False

    @api.onchange('real_estate_sale')
    def _onchange_real_estate_sale(self):
            self.sale_price = False
            self.sale_price_currency = 45
            self.compute_price_fixed_sale = False
            self.compute_price_percentage_sale = False
    
    @api.constrains(
        'total_area',
        'builded_surface',
        'bedroom_quantity',
        'dependencies',
        'cellar',
        'parking',
        'floor_quantity',
        'dep_x_floor',
        'elevator',
        'sale_price',
        'lease_price',
        'common_expenses',
        'contributions',
        'tax_assessment',
        'commercial_appraisal',
        'agreed_commission_fixed',
        'agreed_commission_percent')
    def _check_numeric_values(self):
        """
        Validación para campos numéricos
        """
        for rec in self:
            if rec.total_area and rec.total_area < 0:
                raise exceptions.ValidationError(_("Superficie Total: Valor inválido")) 
            if rec.builded_surface and rec.builded_surface < 0:
                raise exceptions.ValidationError(_("Superficie Construida: Valor inválido"))
            if rec.bedroom_quantity and rec.bedroom_quantity < 0:
                raise exceptions.ValidationError(_("Dormitorios: Valor inválido"))
            if rec.dependencies and rec.dependencies < 0:
                raise exceptions.ValidationError(_("Baños: Valor inválido"))
            if rec.cellar and rec.cellar < 0:
                raise exceptions.ValidationError(_("Bodegas: Valor inválido"))
            if rec.parking and rec.parking < 0:
                raise exceptions.ValidationError(_("Estacionamientos: Valor inválido"))
            if rec.floor_quantity and rec.floor_quantity < 0:
                raise exceptions.ValidationError(_("Cantidad de Pisos: Valor inválido"))
            if rec.dep_x_floor and rec.dep_x_floor < 0:
                raise exceptions.ValidationError(_("Departamentos por Piso: Valor inválido"))
            if rec.elevator and rec.elevator < 0:
                raise exceptions.ValidationError(_("Ascensores: Valor inválido"))
            if rec.sale_price and rec.sale_price < 0:
                raise exceptions.ValidationError(_("Precio de Venta: Valor inválido"))
            if rec.lease_price and rec.lease_price < 0:
                raise exceptions.ValidationError(_("Precio de Arriendo: Valor inválido"))
            if rec.common_expenses and rec.common_expenses < 0:
                raise exceptions.ValidationError(_("Gastos Comunes: Valor inválido"))
            if rec.contributions and rec.contributions < 0:
                raise exceptions.ValidationError(_("Contribuciones: Valor inválido"))
            if rec.tax_assessment and rec.tax_assessment < 0:
                raise exceptions.ValidationError(_("Tasación Fiscal: Valor inválido"))
            if rec.commercial_appraisal and rec.commercial_appraisal < 0:
                raise exceptions.ValidationError(_("Tasación Comercial: Valor inválido"))
            if rec.agreed_commission_fixed and rec.agreed_commission_fixed < 0:
                raise exceptions.ValidationError(_("Comisión Pactada: Valor inválido"))
            if rec.agreed_commission_percent and rec.agreed_commission_percent < 0:
                raise exceptions.ValidationError(_("Comisión Pactada %: Valor inválido"))

    @api.constrains('cons_year')
    def _check_cons_year(self):
        """
        Validación para el campo 'cons_year'
        """
        for record in self:
            if record.cons_year:
                if record.cons_year.isdigit():
                    val_year = int(record.cons_year)
                    if val_year >= 1900.0 and val_year <= 2100.0:
                        pass

                    else:
                        raise exceptions.ValidationError(_("Año de Construcción: No esta en un rango válido"))        
                else:
                    raise exceptions.ValidationError(_("Año de Construcción: Valor inválido"))

    @api.constrains('num_rol')
    def _check_num_rol(self):
        """
        Validación para el campo 'num_rol'
        """
        for record in self:
            if record.num_rol:
                if '-' in record.num_rol:
                    verify_num_rol = record.num_rol.split('-')
                    
                    if verify_num_rol[0].isdigit() and verify_num_rol[1].isdigit():
                        if len(verify_num_rol[0]) == 5 and len(verify_num_rol[1]) == 5:
                            pass

                        else:
                            raise exceptions.ValidationError(_("Número de Rol: Cantidad de números inválido"))
                    else:
                        raise exceptions.ValidationError(_("Número de Rol: Valor inválido"))
                else:
                    if record.num_rol.isdigit():
                        if len(record.num_rol) == 10:
                            pass

                        else:
                            raise exceptions.ValidationError(_("Número de Rol: Cantidad de números inválido"))
                    else:
                        raise exceptions.ValidationError(_("Número de Rol: Valor inválido"))
    
    def _format_num_rol(self, vals):
        """
        Formatea el valor de 'num_rol'
        """
        if 'num_rol' in vals and vals['num_rol'] is not False:
            if not '-' in vals['num_rol']:
                vals['num_rol'] = "{}-{}".format(vals['num_rol'][:5], vals['num_rol'][5:])
    
    def _validate_compute_price(self, vals):
        """
        Validación para Comisión Pactada
        """
        if 'compute_price' in vals:
            if vals['compute_price'] == 'fixed':
                vals['agreed_commission_percent'] = 0.000
            elif vals['compute_price'] == 'percentage':
                vals['agreed_commission_fixed'] = 0.000

    @api.model
    def create(self, vals):
        """
        Crea los registros del módelo
        """

        self._format_num_rol(vals)
        self._validate_compute_price(vals)

        res = super(PropertyManagementProperty, self).create(vals)
        
        return res

    def write(self, vals):
        """
        Edita los registros del módelo
        """

        self._format_num_rol(vals)
        self._validate_compute_price(vals)

        return super(PropertyManagementProperty, self).write(vals)

    def unlink(self):
        """
        Eliminma los registros del módelo
        """
        return super(PropertyManagementProperty, self).unlink()

    
    """
        As the canban view is built with methods from the Odoo kernel, 
        the strategy was to build auxiliary calculated fields where the character "," 
        was added at the end, so as not to have to affect more complex functionalities.
    """

    street_kanban_report = fields.Char(string="Calle", compute="_compute_street_kanban_report")
    street2_kanban_report = fields.Char(string="Calle 2", compute="_compute_street2_kanban_report")
    state_kanban_report = fields.Char(string="State", compute="_compute_state_kanban_report")
    country_kanban_report = fields.Char(string="Country", compute="_compute_country_kanban_report")

    @api.depends('street')
    def _compute_street_kanban_report(self):
        for rec in self:
            if not rec.street:
                rec.street_kanban_report = ''
            else:
                rec.street_kanban_report = rec.street + ','

    @api.depends('street2')
    def _compute_street2_kanban_report(self):
        for rec in self:
            if not rec.street2:
                rec.street2_kanban_report = ''
            else:
                rec.street2_kanban_report = rec.street2 + ','

    @api.depends('state_id')
    def _compute_state_kanban_report(self):
        for rec in self:
            if not rec.state_id:
                rec.state_kanban_report = ''
            else:
                rec.state_kanban_report = rec.state_id.name + ','

    @api.depends('country_id')
    def _compute_country_kanban_report(self):
        for rec in self:
            if not rec.country_id:
                rec.country_kanban_report = ''
            else:
                rec.country_kanban_report = rec.country_id.name

    def get_fields_to_ignore_in_search(self): 
        return ['activity_exception_decoration', 'campaign_id', 'compute_price_lease', 'compute_price_sale', 'address',
                'message_has_sms_error', 'message_has_error', 'evaluation', 'previous_evaluation', 'visits_date',
                'source_id', 'property_maps', 'image_ids', 'medium_id', 'origin', 'origin_name', 'city',
                'external_property', 'price', 'visits', 'activity_type_icon']

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(PropertyManagementProperty, self).fields_get(allfields, attributes=attributes)
        for field in self.get_fields_to_ignore_in_search():
            if res.get(field):
               res.get(field)['searchable'] = False
        return res

class PropertyAttachments(models.Model):
    _description = "Attachments"
    _name = 'property.attachments'

    name = fields.Char("Nombre")
    attachments = fields.Binary("Archivo")
    property_id = fields.Many2one('property.management.property', 'Property')
