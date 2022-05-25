# Copyright 2022 Rosen Vladimirov, BioPrint Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Knowledge Mrp External Docs',
    'summary': """
        Clue between mrp_external_docs and knowledge.""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Rosen Vladimirov, BioPrint Ltd.,Odoo Community Association (OCA)',
    'website': 'https://github.com/rosenvladimirov/knowledge',
    'depends': [
        'knowledge',
        'mrp_external_docs'
    ],
    'data': [
        "data/res_request_link.xml",
        "data/ir_attachment_journal.xml",
        "data/ir_attachment_journal.yml",
        'views/ir_attachment_view.xml',
    ],
    'demo': [
    ],
}
