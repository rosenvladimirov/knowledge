# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Account documents",
    'version': '11.0.4.0.0',
    'category': 'Accounting',
    "author": "Rosen Vladimirov <vladimirov.rosen@gmail.com>, "
              "BioPrint Ltd., "
              "dXFactory Ltd. <http://www.dxfactory.eu>",
    'website': 'https://github.com/rosenvladimirov/account-financial-tools',
    'license': 'AGPL-3',
    "depends": [
        'base',
        'contacts',
        "mail",
            ],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_attachment_view.xml',
        'views/res_partner_view.xml',
            ],
    'installable': True,
}
