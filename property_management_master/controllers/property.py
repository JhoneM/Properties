from odoo import fields, http, _
from odoo.http import request


class WebsiteSaleForm(http.Controller):
    @http.route(
        [
            """/properties""",
            """/properties/page/<int:page>""",
        ],
        type="http",
        auth="public",
        website=True,
    )
    def properties(self, page=0, search="", ppg=4, sortby=None, **post):
        Property = request.env["property.management.property"]
        properties_count = Property.sudo().search_count([])

        pager = request.website.pager(
            url="/properties",
            total=properties_count,
            page=page,
            step=ppg,
            scope=7,
        )

        searchbar_sortings = {
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

        # default sort by order
        if not sortby:
            sortby = "area_max"
        order = searchbar_sortings[sortby]["order"]

        properties = Property.sudo().search(
            [],
            order=order,
            limit=ppg,
            offset=pager["offset"],
        )

        values = {
            "search": search,
            "pager": pager,
            "properties": properties,
        }

        return request.render(
            "property_management_master.properties", values
        )

    @http.route(
        ["/property/<int:property_id>"], type="http", website=True
    )
    def property_details(self, property_id=None, **kw):
        Property = request.env["property.management.property"]
        property_obj = Property.sudo().browse([property_id])
        values = {
            "page_name": "Property",
            "property": property_obj,
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
