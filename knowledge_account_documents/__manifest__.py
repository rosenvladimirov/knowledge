# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Knowledge Management System - Accounting documents",
    "version": "11.0.0.3.0",
    "author": "Rosen Vladimirov, "
              "BioPrint Ltd., "
              "Odoo Community Association (OCA)",
    "category": "Knowledge",
    "license": "AGPL-3",
    "website": "https://github.com/rosenvladimirov/knowledge",
    "depends": [
        "knowledge",
        "account_documents",
    ],
    "data": [
        "data/ir_attachment_journal.xml",
        "data/ir_attachment_journal.yml",
        "views/ir_attachment_view.xml",
    ],
    "demo": [
    ],
    "installable": True,
    "application": True,
}
