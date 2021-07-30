# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

import logging

_logger = logging.getLogger(__name__)


class ExternalDocuments(models.Model):
    _inherit = "external.documents"

    datasheet_ids = fields.One2many('product.manufacturer.datasheets', compute="_compute_datasheet_ids")

    @api.multi
    def _compute_datasheet_ids(self):
        for record in self:
            if not record.datasheet_ids and record.ir_attachment_id:
                # _logger.info("DATAS %s" % record.ir_attachment_id)
                docs = self.env['product.manufacturer.datasheets'].search([('ir_attachment_id', '=', record.ir_attachment_id.id)])
                for att in docs:
                    if record.datasheet_ids:
                        record.datasheet_ids |= att
                    else:
                        record.datasheet_ids = att.ids
