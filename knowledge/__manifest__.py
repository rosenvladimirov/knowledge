# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Knowledge Management System",
    "version": "11.0.4.1.0",
    "author": "Rosen Vladimirov, "
              "OpenERP SA,"
              "MONK Software, "
              "Tecnativa, "
              "Eficent, "
              "Odoo Community Association (OCA)",
    "category": "Knowledge",
    "license": "AGPL-3",
    "website": "https://github.com/rosenvladimirov/knowledge",
    'external_dependencies': {'python': ['pdfminer']},
    "depends": [
        "base",
        "document",
        "queue_job",
    ],
    "data": [
        # "data/knowledge_data.xml", remove the sequence move to create inside
        "data/ir_module_category.xml",
        "data/attachment_stage.xml",
        "data/ir_attachment_journal.xml",
        "data/ir_attachment_journal.yml",
        "security/knowledge_security.xml",
        "security/ir.model.access.csv",
        "views/ir_attachment_view.xml",
        "views/knowledge_template.xml",
        "views/knowledge.xml",
        "views/res_config.xml",
        "views/attachment_stages.xml",
        "views/attachment_dashboard_view.xml",
        "views/ir_attachment_journal_template.xml",
        "views/ir_attachment_journal.xml",
        "views/attachment_journal_category_view.xml",
    ],
    "demo": [
        "demo/knowledge.xml",
    ],
    "installable": True,
    "application": True,
}
