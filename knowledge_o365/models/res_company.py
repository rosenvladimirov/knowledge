# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    oauth_provider_id = fields.Many2one('auth.oauth.provider', string='OAuth Provider')
    o365_drive_id = fields.Char('drive-id')
    o365_user = fields.Char('o365 User')
    o365_password = fields.Char('o365 Password')
