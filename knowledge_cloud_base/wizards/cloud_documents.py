# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
import logging

_logger = logging.getLogger(__name__)


class KnowledgeCloudBaseCloud(models.TransientModel):
    _name = "knowledge.cloud.base.cloud"
    _description = "Holder get from cloud attachment"

    ir_attachment_id = fields.Many2one('ir.attachment', string='Related attachment', required=True)
    cloud_path = fields.Char('Cloud path')

    @api.model
    def default_get(self, fields_list):
        res = super(KnowledgeCloudBaseCloud, self).default_get(fields_list)
        external_document = self.env['external.documents'].browse(self._context.get('default_external_document_id'))
        res.update({
            'ir_attachment_id': external_document.ir_attachment_id and external_document.ir_attachment_id.id or False,
            'cloud_path': external_document.url,
        })
        return res

    @api.multi
    def share_with_from_cloud(self):
        for record in self:
            record.ir_attachment_id.cloud_path = record.cloud_path
            self.ir_attachment_id._share_file_with_link()
        return False
