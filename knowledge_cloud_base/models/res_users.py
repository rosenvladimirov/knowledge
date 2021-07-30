# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo import SUPERUSER_ID


class User(models.Model):
    _inherit = 'res.users'

    cloud_user = fields.Char('Cloud user')

    def __init__(self, pool, cr):
        cr.execute("SELECT column_name FROM information_schema.columns "
                   "WHERE table_name = 'res_users' AND column_name = 'cloud_user'")
        if not cr.fetchone():
            cr.execute('ALTER TABLE res_users '
                       'ADD COLUMN cloud_user character varying;')
        return super(User, self).__init__(pool, cr)
