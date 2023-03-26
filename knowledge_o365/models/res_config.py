# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class NextcloudConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_rmount = fields.Boolean('Use mount with davfs2', related='company_id.use_rmount')
    rclone_url = fields.Char('URL', related='company_id.rclone_url')
    rclone_user = fields.Char('User', related='company_id.rclone_user')
    rclone_password = fields.Char('Password', related='company_id.rclone_password')
    rclone_basic_root = fields.Char('Root dir', related='company_id.rclone_basic_root')
    rclone_port = fields.Integer('rclone Port', related='company_id.rclone_port')

    @api.onchange('use_rmount')
    @api.depends('rclone_url', 'rclone_user', 'rclone_password', 'rclone_basic_root', 'rclone_port')
    def onchange_use_davfs2(self):
        if self.use_davfs2:
            self.nextcloud_url = False
            self.nextcloud_password = False
            self.nextcloud_user = False
            self.rclone_port = 0
