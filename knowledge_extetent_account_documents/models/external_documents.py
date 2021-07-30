# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

import logging

_logger = logging.getLogger(__name__)


class ExternalDocuments(models.Model):
    _inherit = "external.documents"

    document_ids = fields.One2many('account.documents', compute="_compute_document_ids")

    @api.multi
    def _compute_document_ids(self):
        for record in self:
            if not record.document_ids and record.ir_attachment_id:
                docs = self.env['account.documents'].search([('ir_attachment_id', '=', record.ir_attachment_id.id)])
                for att in docs:
                    if record.document_ids:
                        record.document_ids |= att
                    else:
                        record.document_ids = att.ids
