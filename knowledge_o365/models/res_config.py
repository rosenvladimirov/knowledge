# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class O365ConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    o365_drive_id = fields.Char('drive-id', related='company_id.o365_drive_id')
    o365_user = fields.Char('o365 User', related='company_id.o365_user')
    o365_password = fields.Char('o365 Password', related='company_id.o365_password')
    oauth_provider_id = fields.Many2one('auth.oauth.provider', string='OAuth Provider',
                                        related='company_id.oauth_provider_id')
