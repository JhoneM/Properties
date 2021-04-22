from odoo import fields, http, _
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL
from math import ceil, floor

import logging

_logger = logging.getLogger(__name__)

MIN_ADRESS_CHAR = 3
REAL_STATE_OPS = {
    "0": "Todos",
    "1": "Venta",
    "2": "Ariendo",
    "3": "Venta/Ariendo",
}


class TableCompute(object):

    def __init__(self):
        self.table = {}

    def _check_place(self, posx, posy, sizex, sizey, ppr):
        res = True
        for y in range(sizey):
            for x in range(sizex):
                if posx + x >= ppr:
                    res = False
                    break
                row = self.table.setdefault(posy + y, {})
                if row.setdefault(posx + x) is not None:
                    res = False
                    break
            for x in range(ppr):
                self.table[posy + y].setdefault(x, None)
        return res

    def process(self, preperties, ppg=20, ppr=4):
        # Compute preperties positions on the grid
        minpos = 0
        index = 0
        maxy = 0
        x = 0
        for p in preperties:
            x = min(2, ppr)
            y = min(2, ppr)
            if index >= ppg:
                x = y = 1

            pos = minpos
            while not self._check_place(pos % ppr, pos // ppr, x, y, ppr):
                pos += 1
            # if 21st preperties (index 20) and the last line is full (ppr preperties in it), break
            # (pos + 1.0) / ppr is the line where the product would be inserted
            # maxy is the number of existing lines
            # + 1.0 is because pos begins at 0, thus pos 20 is actually the 21st block
            # and to force python to not round the division operation
            if index >= ppg and ((pos + 1.0) // ppr) > maxy:
                break

            if x == 1 and y == 1:   # simple heuristic for CPU optimization
                minpos = pos // ppr

            for y2 in range(y):
                for x2 in range(x):
                    self.table[(pos // ppr) + y2][(pos % ppr) + x2] = False
            self.table[pos // ppr][pos % ppr] = {
                'property': p, 'x': x, 'y': y,
            }
            if index <= ppg:
                maxy = max(maxy, y + (pos // ppr))
            index += 1

        # Format table according to HTML needs
        rows = sorted(self.table.items())
        rows = [r[1] for r in rows]
        for col in range(len(rows)):
            cols = sorted(rows[col].items())
            x += len(cols)
            rows[col] = [r[1] for r in cols if r[1]]

        return rows


class WebsiteSaleForm(http.Controller):

    def get_adress_fields(self):
        return ['name', 'street', 'street2', 'city', 'state_id', 'country_id']

    def get_real_state_operations(self):
        return [
            ("0", _("Todos")),
            ("1", _("Venta")),
            ("2", _("Ariendo")),
            ("3", _("Venta/Ariendo")),
        ]

    def get_search_sortings(self):
        return {
            "date": {
                "label": _("Fecha de Publicación"),
                "order": "create_date asc",
            },
            "price_max": {
                "label": _("Precio Max"),
                "order": "lease_price desc",
            },
            "price_min": {
                "label": _("Precio Min"),
                "order": "lease_price asc",
            },
            "area_max": {
                "label": _("Superficie Max"),
                "order": "total_area desc",
            },
            "area_min": {
                "label": _("Superficie Min"),
                "order": "total_area asc",
            },
        }

    def get_real_state_currency(self):
        return [request.env.ref('base.USD'), request.env.ref('base.CLP'), request.env.ref('base.UF')]

    def get_default_price_range(self, op,  leaf, currency=False, steps=6, granularity=1000):
        company_currency = request.env.company.currency_id
        if currency is False:
            currency = company_currency

        if op == '1':
            min_field = max_field = 'sale_price_company_currency'
        elif op == '2':
            min_field = max_field = 'lease_price_company_currency'
        else:
            min_field = 'lease_price_company_currency'
            max_field = 'sale_price_company_currency'

        min_price = request.env["property.management.property"].search(
            leaf, limit=1, order='%s asc' % min_field)
        max_price = request.env["property.management.property"].search(
            leaf, limit=1, order='%s desc' % max_field)
        if min_price[min_field] >= max_price[max_field]:
            return [(x, "%s %i" % (currency.name, x)) for x in range(20000, 10000000, 100)]
        if len(min_price):
            min_price = floor(min_price[min_field] / granularity) * granularity
        if len(max_price):
            max_price = ceil(max_price[max_field] / granularity) * granularity
        step = ceil((max_price - min_price) /
                    steps / granularity) * granularity
        if company_currency.id == currency.id:
            return [(x, "%s %i" % (currency.name, x)) for x in range(min_price, max_price, step)]
        else:
            res = []
            for x in range(min_price, max_price, step):
                val = currency._convert(
                    x,
                    company_currency,
                    request.env.company,
                    fields.Date.today()
                )
                res.append((int(val), "%s %i" % (currency.name, val)))
            return res

    @http.route(
        [
            """/properties""",
            """/properties/page/<int:page>""",
        ],
        type="http",
        auth="public",
        website=True,
        methods=['GET']
    )
    def properties(self, page=0, ppg=9, sortby=None, currency='', **post):

        property_type_ids = request.env['property.management.type'].search([])
        currency_ids = request.env['res.currency'].search([])
        currency_id = request.env['res.currency']

        if currency != '':
            currency_id = request.env['res.currency'].search(
                [('name', '=', currency)])
        if not len(currency_id):
            currency_id = request.env.company.currency_id

        post['currency_id'] = currency_id
        post['company_currency'] = request.env.company.currency_id

        leaf = self.make_leaf(post)
        op = post['real_state_op'] if 'real_state_op' in post else ''
        price_leaf = self.make_leaf(post, False)
        price_range = self.get_default_price_range(op, price_leaf, currency_id)

        keep = QueryURL('/properties',
                        real_state_op=post.get('real_state_op'),
                        currency=currency,
                        property_type_id=post.get('property_type_id'),
                        amount_min=post.get('amount_min'),
                        amount_max=post.get('amount_max'))

        Property = request.env["property.management.property"]
        properties_count = Property.search_count(leaf)
        pager = request.website.pager(
            url="/properties",
            total=properties_count,
            page=page,
            step=ppg,
            scope=7,
            url_args=post,
        )

        searchbar_sortings = self.get_search_sortings()

        # default sort by order
        if not sortby:
            sortby = "area_max"
        order = searchbar_sortings[sortby]["order"]

        properties = Property.search(
            leaf,
            order=order,
            limit=ppg,
            offset=pager["offset"],
        )
        values = {
            "pager": pager,
            "properties": properties,
            "property_type_ids": property_type_ids,
            "currency_ids": currency_ids,
            "currency": currency_id,
            "operations": self.get_real_state_operations(),
            "amount_min": price_range[:-1],
            "amount_max": price_range[1:],
            'get_vals': post,
            'keep': keep,
            "searchbar_sortings": searchbar_sortings,
            "selected_sort": sortby,        }
        return request.render(
            "property_management_master.properties", values
        )

    def make_leaf(self, vals, add_amount=True):
        leaf = []
        op = False
        if vals.get('real_state_op', False) and vals['real_state_op'] in ['1', '2', '3']:
            op = 'both'

            if vals['real_state_op'] == '1':
                leaf.append(('real_estate_lease', '=', True))
                op = 'lease'
            elif vals['real_state_op'] == '2':
                leaf.append(('real_estate_sale', '=', True))
                op = 'sale'
            elif vals['real_state_op'] == '3':
                leaf.append(('real_estate_sale', '=', True))
                leaf.append(('real_estate_lease', '=', True))

        if vals.get('total_area_min', False):
            leaf.append(('total_area', '>=', float(
                vals['total_area_min'].replace(',', '.'))))

        if vals.get('total_area_max', False):
            leaf.append(('total_area', '<=', float(
                vals['total_area_max'].replace(',', '.'))))

        if vals.get('bedroom_quantity_min', False):
            leaf.append(('bedroom_quantity', '>=', int(
                vals['bedroom_quantity_min'])))

        if vals.get('bedroom_quantity_max', False):
            leaf.append(('bedroom_quantity' '<=', int(
                vals['bedroom_quantity_max'])))

        if vals.get('dependecies_min', False):
            leaf.append(('dependecies', '>=', int(vals['dependecies_min'])))

        if vals.get('dependecies_max', False):
            leaf.append(('dependecies' '<=', int(vals['dependecies_max'])))

        if vals.get('property_type_id', False) and vals['property_type_id'].isnumeric():
            leaf.append(('type_id', '=', int(vals['property_type_id'])))

        if vals.get('amount_min', False) and add_amount:
            if vals['currency_id'].id != vals['company_currency'].id:
                amount_min = vals['company_currency']._convert(
                    float(vals['amount_min']),
                    vals['currency_id'],
                    request.env.company,
                    fields.Date.today()
                )
            else:
                amount_min = float(vals['amount_min'])

            if op != 'lease':
                leaf.append(('sale_price_company_currency', '>=', amount_min))
            if op != 'sale':
                leaf.append(('lease_price_company_currency', '>=', amount_min))

        if vals.get('amount_max', False) and add_amount:
            if vals['currency_id'].id != vals['company_currency'].id:
                amount_max = vals['company_currency']._convert(
                    float(vals['amount_max']),
                    vals['currency_id'],
                    request.env.company,
                    fields.Date.today()
                )
            else:
                amount_max = float(vals['amount_max'])

            if op != 'lease':
                leaf.append(('lease_price_company_currency', '<=',
                             amount_max))
            elif op != 'sale':
                leaf.append(('lease_price_company_currency', '<=', amount_max))

        if vals.get('address', False) and len(vals['address'].strip()) > MIN_ADRESS_CHAR:
            address_words = vals['address'].strip().replace(',', ' ').split()
            for word in address_words:
                if len(word) > MIN_ADRESS_CHAR:
                    leaf.append(('address_text', 'ilike', '%%%s%%' % word))
        _logger.info(leaf)
        return leaf

    @http.route(
        ["/property/<model('property.management.property'):property_id>"],
        type="http",
        website=True,
        auth="public")
    def property_details(self, property_id, **kw):
        values = {
            "page_name": "Property",
            "property": property_id,
        }

        if kw.get("error"):
            values["error"] = kw["error"]
        if kw.get("warning"):
            values["warning"] = kw["warning"]
        if kw.get("success"):
            values["success"] = kw["success"]

        return request.render(
            "property_management_master.property_page", values
        )
