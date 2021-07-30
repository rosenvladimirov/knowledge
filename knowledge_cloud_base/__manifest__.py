# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Knowledge Management System - Cloud clue",
    "version": "11.0.0.2.0",
    "author": "Rosen Vladimirov, "
              "BioPrint Ltd., "
              "Odoo Community Association (OCA)",
    "category": "Knowledge",
    "license": "AGPL-3",
    "website": "https://github.com/rosenvladimirov/knowledge",
    "depends": [
        "knowledge",
        "cloud_base",
        "product_properties",
        "account_documents",
        "external_documents",
        "knowledge_account_documents",
        "knowledge_external_attachment",
    ],
    "data": [
        "views/res_users_view.xml",
        "wizards/external_documents.xml",
        "wizards/account_documents.xml",
        "wizards/cloud_documents.xml",
        "views/ir_attachment_view.xml",
    ],
    "demo": [
    ],
    "installable": True,
    "application": True,
}
