# Copyright 2022 Rosen Vladimirov, BioPrint Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Knowledge Rclone',
    'summary': """
        Add suppert for rclone""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Rosen Vladimirov, BioPrint Ltd.,Odoo Community Association (OCA)',
    'website': 'https://github.com/rosenvladimirov/knowledge',
    'depends': [
        'base',
        'knowledge',
        'external_documents',
    ],
    'data': [
        'views/res_config.xml',
    ],
    'demo': [
    ],
}
