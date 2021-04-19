# -*- coding: utf-8 -*-
{
    "name": "Property Management",
    "summary": """
        Integración Property Management
    """,
    "description": """
        Módulo Integración Property Management
    """,
    "author": "cgimenez@persiscalconsulting.com",
    "website": "https://www.persiscalconsulting.com",
    "category": "Property_Management/Property_Management",
    "version": "1.0",
    "depends": [
        "website_form",
        "base",
        "crm",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/property_management_state_data.xml",
        "data/property_management_type_data.xml",
        "data/property_management_origin_data.xml",
        "views/property_view.xml",
        "views/state_view.xml",
        "views/type_view.xml",
        "views/amb_view.xml",
        "views/tag_view.xml",
        "views/orientation_view.xml",
        "views/image_view.xml",
        "views/res_partner_view.xml",
        "views/crm_lead_view.xml",
        "views/menu_view.xml",
        "views/property_map.xml",
        "views/property_origin.xml",
        "views/property_template.xml",
        "views/templates.xml"
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
