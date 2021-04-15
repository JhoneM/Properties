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
    def properties(self, page=0, search="", ppg=2, **post):
        Property = request.env["property.management.property"]
        properties_count = Property.sudo().search_count([])

        pager = request.website.pager(
            url="/properties",
            total=properties_count,
            page=page,
            step=3,
            scope=7,
        )
        properties = Property.sudo().search(
            [],
            limit=3,
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
