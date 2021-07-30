# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import time

from odoo import api, fields, models, tools, _
# from odoo.addons.account.models.account_invoice import TYPE2REFUND
from odoo.exceptions import Warning as UserWarning, UserError
from odoo.tools.safe_eval import safe_eval

import logging

_logger = logging.getLogger(__name__)


class AccountDocuments(models.Model):
    _inherit = "account.documents"

    external_document_ids = fields.One2many('external.documents', compute="_compute_document_ids")

    @api.multi
    def _compute_document_ids(self):
        for record in self:
            if not record.external_document_ids and record.ir_attachment_id:
                # _logger.info("DATAS %s" % record.ir_attachment_id)
                docs = self.env['external.documents'].search([('ir_attachment_id', '=', record.ir_attachment_id.id)])
                for att in docs:
                    if record.external_document_ids:
                        record.external_document_ids |= att
                    else:
                        record.external_document_ids = att.ids

    @api.model
    def create(self, vals):
        res = super(AccountDocuments, self).create(vals)
        docs = self.env['external.documents'].search([('ir_attachment_id', '=', res.ir_attachment_id.id)])
        if not docs:
            ctx = self._context.copy()
            att = self.env[res.res_model].browse(res.res_id)
            partners = self.env['external.documents'].search_documents_for_partner(att)
            values = {'ir_attachment_id': res.ir_attachment_id.id, 'company_id': res.company_id.id}
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
        res = super(AccountDocuments, self).write(vals)
        for record in self:
            docs = self.env['external.documents'].search([('ir_attachment_id', '=', record.ir_attachment_id.id)])
            if not docs:
                ctx = self._context.copy()
                att = self.env[record.res_model].browse(record.res_id)
                partners = self.env['external.documents'].search_documents_for_partner(att)
                values = {'ir_attachment_id': record.ir_attachment_id.id, 'company_id': record.company_id.id}

                if partners:
                    ctx.update({'block_res': True})
                    for partner in list(partners):
                        values.update({'partner_id': partner.id})
                        docs.with_context(ctx).create(values)
        return res

    @api.multi
    def add_external_document(self):
        for record in self:
            ctx = self._context.copy()
            att = self.env[record.res_model].browse(record.res_id)
            partners = self.env['external.documents'].search_documents_for_partner(att)
            values = {'ir_attachment_id': record.ir_attachment_id.id, 'company_id': record.company_id.id}

            if partners:
                ctx.update({'block_res': True})
                for partner in list(partners):
                    values.update({'partner_id': partner.id})
                    self.env['external.documents'].with_context(ctx).create(values)
