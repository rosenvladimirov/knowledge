# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class ProductManufacturerDatasheets(models.Model):
    _inherit = 'product.manufacturer.datasheets'

    external_document_ids = fields.One2many('external.documents', compute="_compute_external_document_ids")

    @api.multi
    def _compute_external_document_ids(self):
        for record in self:
            if not record.external_document_ids and record.ir_attachment_id:
                docs = self.env['external.documents'].search([('ir_attachment_id', '=', record.ir_attachment_id.id)])
                for att in docs:
                    if record.external_document_ids:
                        record.external_document_ids |= att
                    else:
                        record.external_document_ids = att.ids

    @api.model
    def create(self, vals):
        res = super(ProductManufacturerDatasheets, self).create(vals)
        if res.res_model == 'res.partner':
            docs = self.env['external.documents'].search([('ir_attachment_id', '=', res.ir_attachment_id.id),
                                                          ('res_model', '=', 'res.partner'),
                                                          ('partner_id', '=', res.res_id)])
            if not docs:
                ctx = self._context.copy()
                att = self.env[res.res_model].browse(res.res_id)
                partners = self.env['external.documents'].search_documents_for_partner(att)
                values = {'ir_attachment_id': res.ir_attachment_id.id}
                if 'company_id' in att._fields:
                    values.update({
                        'company_id': att.company_id.id,
                    })
                if partners:
                    ctx.update({'block_res': True})
                    for partner in list(partners):
                        values.update({'partner_id': partner.id})
                        docs.with_context(ctx).create(values)
        return res

    @api.multi
    def write(self, vals):
        res = super(ProductManufacturerDatasheets, self).write(vals)
        for record in self:
            if record.res_model == 'res.partner':
                docs = self.env['external.documents'].search([('ir_attachment_id', '=', record.ir_attachment_id.id),
                                                              ('res_model', '=', 'res.partner'),
                                                              ('partner_id', '=', record.res_id)])
                if not docs:
                    ctx = self._context.copy()
                    att = self.env[record.res_model].browse(record.res_id)
                    partners = self.env['external.documents'].search_documents_for_partner(att)
                    values = {'ir_attachment_id': record.ir_attachment_id.id}

                    if partners:
                        ctx.update({'block_res': True})
                        for partner in list(partners):
                            values.update({'partner_id': partner.id})
                            docs.with_context(ctx).create(values)
        return res

    @api.multi
    def add_external_documents(self):
        for record in self:
            ctx = self._context.copy()
            att = self.env[record.res_model].browse(record.res_id)
            partners = self.env['external.documents'].search_documents_for_partner(att)
            values = {'ir_attachment_id': record.ir_attachment_id.id}

            if partners:
                ctx.update({'block_res': True})
                for partner in list(partners):
                    values.update({'partner_id': partner.id})
                    self.env['external.documents'].with_context(ctx).create(values)
            else:
                raise UserError("Try adding this in an external document to the same partner in the current document")
