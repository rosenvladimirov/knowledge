# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    use_rmount = fields.Boolean('Use mount with rclone')
    rclone_url = fields.Char('URL')
    rclone_port = fields.Integer('Port')
    rclone_user = fields.Char('User')
    rclone_password = fields.Char('Password')
    rclone_basic_root = fields.Char('Root dir')
