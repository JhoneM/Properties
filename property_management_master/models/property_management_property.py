# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _

import logging

_logger = logging.getLogger(__name__)

URL_API_MAPS = '<img id="map" src="https://maps.googleapis.com/maps/api/staticmap?zoom={}&size=400x400&markers=color:red%7Clabel:P%7C{}&key={}"/>'


class PropertyManagementProperty(models.Model):
    _description = "Propiedad"
    _name = 'property.management.property'
    _inherit = ['mail.thread.cc',
                'mail.activity.mixin',
                'utm.mixin',
                'image.mixin',
                'website.seo.metadata',
                'website.published.mixin'
                ]

    name = fields.Char(_('Nombre'), index=True)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
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

    active = fields.Boolean(
        string='Active',
        default=True
    )
    state_prop_id = fields.Many2one(
        'property.management.state',
        group_expand='_read_group_stage_ids',
        string=_('Estado'),
        default=_get_default_state_prop_id
    )
    type_id = fields.Many2one(
        'property.management.type',
        string=_('Tipo'),
        index=True,
        ondelete='cascade'
    )
    total_area = fields.Integer(
        string=_("Superficie total")
    )
    builded_surface = fields.Integer(
        string=_("Superficie construida")
    )
    partner_id = fields.Many2one(
        'res.partner',
        string=_("Contacto"),
        index=True
    )
    cons_year = fields.Char(
        string=_("Año de construcción")
    )
    num_rol = fields.Char(
        string=_("Número de rol")
    )
    street = fields.Char(
        string=_("Calle")
    )
    street2 = fields.Char(
        string=_("Calle 2")
    )
    zip = fields.Char(
        string=_("C.P.")
    )
    city = fields.Char(
        string=_("Comuna")
    )
    state_id = fields.Many2one(
        "res.country.state",
        string='Región',
        ondelete='restrict',
        domain="[('country_id', '=?', country_id)]"
    )
    country_id = fields.Many2one(
        'res.country',
        string='País',
        ondelete='restrict'
    )
    address_text = fields.Text(
        string='address',
        compute='_compute_address',
        store=True,
    )
    amb_ids = fields.Many2many(
        'property.management.amb',
        string=_("Espacios")
    )
    bedroom_quantity = fields.Integer(
        string=_("Dormitorios")
    )
    dependencies = fields.Integer(
        string=_("Baños")
    )
    cellar = fields.Integer(
        string=_("Bodegas")
    )
    parking = fields.Integer(
        string=_("Estacionamientos")
    )
    orientation_id = fields.Many2one(
        'property.management.orientation',
        string=_('Orientación'),
        index=True,
        ondelete='cascade'
    )
    tag_ids = fields.Many2many(
        'property.management.tag',
        string=_("Características")
    )
    community_name = fields.Char(
        string=_("Nombre comunidad")
    )
    construction_company_id = fields.Many2one(
        'res.partner',
        string=_("Constructora"),
        index=True,
    )
    floor_quantity = fields.Integer(
        string=_("Cantidad de pisos")
    )
    dep_x_floor = fields.Integer(
        string=_("Departamentos por piso")
    )
    num_floor = fields.Char(
        string=_("Piso")
    )
    elevator = fields.Integer(
        string=_("Ascensores")
    )
    image_ids = fields.One2many(
        'property.management.property.image',
        'property_parent_id',
        'Imagenes de la propiedad'
    )
    expiration_date = fields.Date(
        'Fecha de Vencimiento'
    )
    origin = fields.Selection(
        [('external', 'Externa'),
         ('employee', 'Empleado')]
    )
    origin_property = fields.Many2one(
        'property.management.origin',
        'Origen'
    )
    origin_name = fields.Char(
        'Origin',
        compute='_compute_origin_name',
        store=True
    )
    broker = fields.Many2one(
        'res.partner',
        'Corredora',
        domain=[("is_broker", "=", "True")]
    )
    employee = fields.Many2one(
        'hr.employee',
        'Empleado'
    )
    key = fields.Boolean(
        'Llaves'
    )
    head = fields.Char(
        'Encabezado'
    )
    description = fields.Text(
        'Descripción'
    )
    attachments = fields.One2many(
        'property.attachments',
        'property_id',
        string='Adjuntos'
    )

    property_maps = fields.Html(
        'Image Html',
        store=True
    )
    property_coordenada = fields.Char(
        "Coordenadas"
    )

    zoom = fields.Selection(selection=[('10', '10'), ('11', '11'), ('12', '12'),
                                       ('13', '13'), ('14', '14'), ('15', '15'),
                                       ('16', '16'), ('17', '17'), ('18', '18'),
                                       ('19', '19'), ('20', '20')],
                            string="Zoom",
                            default="15"
                            )

    @api.depends('name', 'street', 'street2', 'city', 'state_id', 'country_id')
    def _compute_address(self):
        for record in self:
            address_format = "%(name)s\n %(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"
            args = {
                'street': record.street,
                'street2': record.street2,
                'state_code': record.state_id.code or '',
                'state_name': record.state_id.name or '',
                'city': record.city or '',
                'country_code': record.country_id.code or '',
                'zip': record.zip or '',
                'country_name': record.country_id.display_name,
                'name': record.name,
            }
            record.address_text = address_format % args

    @api.depends('origin_property')
    def _compute_origin_name(self):
        for rec in self:
            rec.origin_name = rec.origin_property.name

    @api.onchange('property_coordenada')
    def _onchange_property_coordenada(self):
        key = self.env['ir.config_parameter'].sudo(
        ).get_param('property_maps.key')
        self.property_maps = URL_API_MAPS.format(
            str(self.zoom), str(self.property_coordenada), str(key))

    @api.onchange('zoom')
    def _onchange_zoom(self):
        key = self.env['ir.config_parameter'].sudo(
        ).get_param('property_maps.key')
        self.property_maps = URL_API_MAPS.format(
            str(self.zoom), str(self.property_coordenada), str(key))

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

        currency_ids = [rec.id for rec in find_currency]
        return [('id', 'in', currency_ids)]

    @api.depends('total_area', 'bedroom_quantity', 'dependencies')
    def compute_display_attributes(self):
        """
        Formatea el valor de 'attributes'
        """
        for rec in self:
            rec.attributes = "<span class='fa fa-bed'>{}</span><br><span class='fa fa-bath'>{}</span><br><span class='fa fa-arrows-alt'>{}</span>".format(
                rec.bedroom_quantity, rec.dependencies, rec.total_area)

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

    @api.depends('sale_price', 'sale_price_currency', 'lease_price', 'lease_price_currency', 'real_estate_sale', 'real_estate_lease')
    def compute_display_price(self):
        """
        Formatea el valor de 'price'
        """
        for rec in self:
            if rec.real_estate_sale:
                rec.price = "<p>{}<br>{}</p>".format(
                    rec.sale_price, rec.sale_price_currency.name)
            else:
                rec.price = "<p>{}<br>{}</p>".format(
                    rec.lease_price, rec.lease_price_currency.name)

    @api.depends('street', 'street2', 'zip', 'city', 'state_id', 'country_id')
    def compute_display_address(self):
        """
        Formatea el valor de 'address'
        """
        for rec in self:
            address = "<p>"
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
                address = address + rec.country_id.name + "<br>"
            rec.address = address + "<p>"

    sale_price = fields.Float(
        string=_("Precio de venta"),
        digits=(16, 3)
    )
    sale_price_currency = fields.Many2one(
        'res.currency',
        string=_("Moneda"),
        domain=_get_currency,
        default=_default_currency
    )
    lease_price = fields.Float(
        string=_("Precio de arriendo"),
        digits=(16, 3)
    )
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
    lease_price_currency = fields.Many2one(
        'res.currency',
        string=_("Moneda"),
        domain=_get_currency,
        default=_default_currency
    )
    tax_assessment = fields.Float(
        string=_("Tasación fiscal"),
        digits=(16, 3)
    )
    tax_assessment_currency = fields.Many2one(
        'res.currency',
        default=_default_currency
    )
    commercial_appraisal = fields.Float(
        string=_("Tasación comercial"),
        digits=(16, 3)
    )
    commercial_appraisal_currency = fields.Many2one(
        'res.currency',
        domain=_get_currency,
        default=_default_currency
    )
    common_expenses = fields.Float(
        string=_("Gastos comunes"),
        digits=(16, 3)
    )
    common_expenses_currency = fields.Many2one(
        'res.currency',
        domain=_get_currency,
        default=_default_currency
    )
    contributions = fields.Float(
        string=_("Contribuciones"),
        digits=(16, 3)
    )
    contributions_currency = fields.Many2one(
        'res.currency',
        domain=_get_currency,
        default=_default_currency
    )
    exclusiveness = fields.Boolean(
        string=_("Exclusividad")
    )
    external_property = fields.Boolean(
        string=_("Origen externo")
    )
    visiting_hours = fields.Char(
        string=_("Horario de visita")
    )
    sign = fields.Boolean(
        string=_("Firma")
    )
    agreed_commission_currency = fields.Many2one('res.currency',
                                                 string=_("Moneda"),
                                                 domain=_get_currency,
                                                 default=_default_currency
                                                 )
    agreed_commission_fixed = fields.Float(
        string=_("Precio fijo"),
        digits=(16, 3)
    )
    agreed_commission_percent = fields.Float(
        string=_("Porcentaje"),
        digits=(16, 3)
    )
    compute_price = fields.Selection([
        ('fixed', 'Precio fijo'),
        ('percentage', 'Porcentaje'), ],
        string=_("Comisión Pactada"),
        index=True,
        default='fixed',
        required=True
    )
    virtual_tour = fields.Char(
        string=_("Tour virtual")
    )
    video = fields.Char(
        string=_("Video")
    )
    # partner_latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    # partner_longitude = fields.Float(string='Geo Longitude', digits=(16, 5))

    amenities = fields.Many2many(
        "property.amenities",
        string="Amenities"
    )
    restrictions = fields.Many2many(
        "property.restrictions",
        string="Restricciones"
    )
    real_estate_lease = fields.Boolean("Arriendo")
    real_estate_sale = fields.Boolean("Venta")
    real_estate_agent = fields.Many2one("hr.employee",
                                        string="Agente"
                                        )
    address = fields.Html(string="Dirección",
                          store=True,
                          compute='compute_display_address'
                          )
    price = fields.Html(
        string="Precio",
        compute='compute_display_price',
        store=True
    )
    attributes = fields.Html(
        string="Atributos",
        compute='compute_display_attributes',
        store=True
    )
    evaluation = fields.Selection(
        [('0', 'Cero'),
         ('1', 'Primero'),
         ('2', 'Segundo'),
         ('3', 'Tercero')]
    )
    visits = fields.Boolean(
        string="Visitas",
        compute='compute_visits',
        store=True
    )
    visits_date = fields.Date(string="Fecha de visitas")
    previous_evaluation = fields.Selection(
        [('0', 'Cero'),
         ('1', 'Primero'),
         ('2', 'Segundo'),
         ('3', 'Tercero')]
    )
    pivot_evaluation = fields.Selection(
        [('0', 'Cero'),
         ('1', 'Primero'),
         ('2', 'Segundo'),
         ('3', 'Tercero')]
    )
    visits_order = fields.Binary("Orden de visita")

    def _compute_website_url(self):
        for record in self:
            record.website_url = "/property/%s" % (record.id)

    @api.onchange('evaluation')
    def _onchange_evaluation(self):
        for rec in self:
            rec.previous_evaluation = rec.pivot_evaluation
            rec.pivot_evaluation = rec.evaluation

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
                raise exceptions.ValidationError(
                    _("Superficie total: Valor inválido"))
            if rec.builded_surface and rec.builded_surface < 0:
                raise exceptions.ValidationError(
                    _("Superficie construida: Valor inválido"))
            if rec.bedroom_quantity and rec.bedroom_quantity < 0:
                raise exceptions.ValidationError(
                    _("Dormitorios: Valor inválido"))
            if rec.dependencies and rec.dependencies < 0:
                raise exceptions.ValidationError(_("Baños: Valor inválido"))
            if rec.cellar and rec.cellar < 0:
                raise exceptions.ValidationError(_("Bodegas: Valor inválido"))
            if rec.parking and rec.parking < 0:
                raise exceptions.ValidationError(
                    _("Estacionamientos: Valor inválido"))
            if rec.floor_quantity and rec.floor_quantity < 0:
                raise exceptions.ValidationError(
                    _("Cantidad de pisos: Valor inválido"))
            if rec.dep_x_floor and rec.dep_x_floor < 0:
                raise exceptions.ValidationError(
                    _("Departamentos por piso: Valor inválido"))
            if rec.elevator and rec.elevator < 0:
                raise exceptions.ValidationError(
                    _("Ascensores: Valor inválido"))
            if rec.sale_price and rec.sale_price < 0:
                raise exceptions.ValidationError(
                    _("Precio de venta: Valor inválido"))
            if rec.lease_price and rec.lease_price < 0:
                raise exceptions.ValidationError(
                    _("Precio de arriendo: Valor inválido"))
            if rec.common_expenses and rec.common_expenses < 0:
                raise exceptions.ValidationError(
                    _("Gastos comunes: Valor inválido"))
            if rec.contributions and rec.contributions < 0:
                raise exceptions.ValidationError(
                    _("Contribuciones: Valor inválido"))
            if rec.tax_assessment and rec.tax_assessment < 0:
                raise exceptions.ValidationError(
                    _("Tasación fiscal: Valor inválido"))
            if rec.commercial_appraisal and rec.commercial_appraisal < 0:
                raise exceptions.ValidationError(
                    _("Tasación comercial: Valor inválido"))
            if rec.agreed_commission_fixed and rec.agreed_commission_fixed < 0:
                raise exceptions.ValidationError(
                    _("Comisión Pactada: Valor inválido"))
            if rec.agreed_commission_percent and rec.agreed_commission_percent < 0:
                raise exceptions.ValidationError(
                    _("Comisión Pactada %: Valor inválido"))

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
                        raise exceptions.ValidationError(
                            _("Año de construcción: No esta en un rango valido"))
                else:
                    raise exceptions.ValidationError(
                        _("Año de construcción: Valor inválido"))

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
                            raise exceptions.ValidationError(
                                _("Número de rol: Cantidad de números inválido"))
                    else:
                        raise exceptions.ValidationError(
                            _("Número de rol: Valor inválido"))
                else:
                    if record.num_rol.isdigit():
                        if len(record.num_rol) == 10:
                            pass

                        else:
                            raise exceptions.ValidationError(
                                _("Número de rol: Cantidad de números inválido"))
                    else:
                        raise exceptions.ValidationError(
                            _("Número de rol: Valor inválido"))

    def _format_num_rol(self, vals):
        """
        Formatea el valor de 'num_rol'
        """
        if 'num_rol' in vals and vals['num_rol'] is not False:
            if not '-' in vals['num_rol']:
                vals[
                    'num_rol'] = "{}-{}".format(vals['num_rol'][:5], vals['num_rol'][5:])

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

    street_kanban_report = fields.Char(
        string="Calle",
        compute="_compute_street_kanban_report"
    )
    street2_kanban_report = fields.Char(
        string="Calle 2",
        compute="_compute_street2_kanban_report"
    )
    state_kanban_report = fields.Char(
        string="State",
        compute="_compute_state_kanban_report"
    )

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


class Propertyamenities(models.Model):
    _description = "amenities"
    _name = 'property.amenities'

    name = fields.Char("Amenite")
    description = fields.Char("Description")


class PropertyRestrictions(models.Model):
    _description = "Restricciones"
    _name = 'property.restrictions'

    name = fields.Char("Restriction")
    description = fields.Char("Description")


class PropertyAttachments(models.Model):
    _description = "Attachments"
    _name = 'property.attachments'

    name = fields.Char("Nombre")
    attachments = fields.Binary("Archivo")
    property_id = fields.Many2one('property.management.property', 'Property')


class PropertyManagementOrigin(models.Model):
    _description = "Origen Propiedades"
    _name = 'property.management.origin'

    name = fields.Char('Origen')
    no_editable = fields.Boolean('Campo No Editable')

    @api.onchange('name')
    def _onchange_name(self):
        if self.no_editable:
            raise exceptions.ValidationError(
                _("No puede modificar este valor."))
