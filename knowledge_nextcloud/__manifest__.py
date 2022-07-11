# Copyright 2022 Rosen Vladimirov, BioPrint Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Knowledge Nextcloud',
    'summary': """
        Add support for nextcloud file store.""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Rosen Vladimirov, BioPrint Ltd.,Odoo Community Association (OCA)',
    'website': 'https://github.com/rosenvladimirov/knowledge',
    'depends': [
        'base',
        'knowledge',
    ],
    'external_dependencies': {
        'python': {'nextcloud_client'},
    },
    'data': [
        'views/res_config.xml',
    ],
    'demo': [
    ],
}
