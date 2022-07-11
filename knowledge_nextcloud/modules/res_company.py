# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    use_davfs2 = fields.Boolean('Use mount with davfs2')
    nextcloud_url = fields.Char('URL')
    nextcloud_user = fields.Char('User')
    nextcloud_password = fields.Char('Password')
    nextcloud_basic_root = fields.Char('Root dir')
