# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Knowledge Management System - External documents",
    "version": "11.0.0.1.0",
    "author": "Rosen Vladimirov, "
              "BioPrint Ltd., "
              "Odoo Community Association (OCA)",
    "category": "Knowledge",
    "license": "AGPL-3",
    "website": "https://github.com/rosenvladimirov/knowledge",
    "depends": [
        "knowledge",
        "external_documents",
        # "crm",
    ],
    "data": [
        "data/res_request_link.xml",
        "data/ir_attachment_journal.xml",
        "data/ir_attachment_journal.yml",
        "views/ir_attachment_view.xml",
    ],
    "demo": [
    ],
    "installable": True,
}
