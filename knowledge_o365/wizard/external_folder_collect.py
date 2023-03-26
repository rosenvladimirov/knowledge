# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WizExternalDocumentsProcess(models.TransientModel):
    _name = 'wiz.external.documents.process'
    _description = 'Process to synchronise external folders'

    o365_folder_id = fields.Many2one('external.folders', string='External folder')

    @api.multi
    def action_collect_external_folders(self):
        self.ensure_one()
        res = self.env['external.folders'].update_folders(limit=10)
        action = self.env.ref('knowledge_o365.external_folders_action_form').read()[0]
        action['domain'] = [('id', 'in', res.ids)]
        return action
