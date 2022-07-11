# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class NextcloudConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_davfs2 = fields.Boolean('Use mount with davfs2', related='company_id.use_davfs2')
    nextcloud_url = fields.Char('URL', related='company_id.nextcloud_url')
    nextcloud_user = fields.Char('User', related='company_id.nextcloud_user')
    nextcloud_password = fields.Char('Password', related='company_id.nextcloud_password')
    nextcloud_basic_root = fields.Char('Root dir', related='company_id.nextcloud_basic_root')

    @api.onchange('use_davfs2')
    @api.depends('nextcloud_url', 'nextcloud_user', 'nextcloud_password', 'nextcloud_basic_root')
    def onchange_use_davfs2(self):
        if self.use_davfs2:
            self.nextcloud_url = False
            self.nextcloud_password = False
            self.nextcloud_user = False
