# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
import logging

_logger = logging.getLogger(__name__)


class KnowledgeCloudBaseExternal(models.TransientModel):
    _name = "knowledge.cloud.base.external"
    _description = "Holder for sharing clued attachment"

    ir_attachment_id = fields.Many2one('ir.attachment', string='Related attachment', required=True)
    users = fields.Many2many('res.users', string='Share with')

    @api.model
    def default_get(self, fields_list):
        res = super(KnowledgeCloudBaseExternal, self).default_get(fields_list)
        external_document = self.env['external.documents'].browse(self._context.get('default_external_document_id'))
        res.update({
            'ir_attachment_id': external_document.ir_attachment_id and external_document.ir_attachment_id.id or False,
            'users': [(6, 0, external_document.responsible_user_ids.ids)],
        })
        return res

    @api.multi
    def share_with_user_external(self):
        for record in self:
            if record.users:
                for user in record.users:
                    self.ir_attachment_id._share_file_with_user(user=user.cloud_user)
        return False
