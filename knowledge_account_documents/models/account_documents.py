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

    def _get_default_attachment_journal_id(self):
        if self._context.get('default_attachment_journal_id'):
            return self._context['default_attachment_journal_id']
        else:
            return self.env['ir.attachment.journal'].search([('company_id', '=', self.env.user.company_id.id),
                                                             ('journal_type', '=', 'documents')], limit=1)

    def _get_domain_type(self):
        return [('display', '=', True)]

    @api.multi
    def _links_get(self):
        link_obj = self.env['res.request.link']
        return [(r.object, r.name) for r in link_obj.search([('object', 'in', ['sale.order', 'purchase.order',
                                                                               'stock.picking', 'account.invoice',
                                                                               'account.bank.statement',
                                                                               'account.invoice.protocol'])])]

    attachment_journal_id = fields.Many2one('ir.attachment.journal', string='Attachment Journal', required=True,
                                            ondelete='cascade', default=_get_default_attachment_journal_id)
    object_id = fields.Reference(string='Reference object', selection=_links_get, )

    @api.model
    def create(self, vals):
        if 'attachment_journal_id' not in vals:
            if self._context.get('attachment_journal'):
                attachment_journal_id = self.env['ir.attachment.journal'].browse(self._context['attachment_journal'])
            elif 'company_id' in vals:
                attachment_journal_id = self.env['ir.attachment.journal'].search(
                    [('company_id', '=', vals['company_id']),
                     ('journal_type', '=', 'documents')],
                    limit=1)
            else:
                attachment_journal_id = self.env['ir.attachment.journal'].search([('company_id', '=', self.env.user.company_id.id),
                                                                                  ('journal_type', '=', 'documents')],
                                                                                 limit=1)
            if attachment_journal_id:
                vals['attachment_journal_id'] = attachment_journal_id.id
            else:
                raise UserWarning("I can't find a journal of accounting documents. Probably deleted from the system...")

        if vals.get('ref', _('New')) == _('New') and 'attachment_journal_id' in vals:
            if 'company_id' in vals:
                vals['ref'] = self.env['ir.sequence'].with_context(
                    force_company=vals['company_id']).next_by_code('ir.attachment.documents') or _('New')
            else:
                vals['ref'] = self.env['ir.sequence'].next_by_code('ir.attachment.documents') or _('New')

        if 'object_id' in vals and vals['object_id']:
            vals['res_model'], vals['res_id'] = tuple(vals['object_id'].split(','))
            vals['res_id'] = int(vals['res_id'])
        if not vals.get('object_id') and 'res_model' in vals and 'res_id' in vals:
            vals['object_id'] = "%s,%s" % (vals['res_model'], vals['res_id'])
        if vals.get('ir_attachment_id') and not vals.get('object_id'):
            attachment = self.env['ir.attachment'].browse(vals['ir_attachment_id'])
            if attachment:
                vals['object_id'] = "%s,%s" % (attachment.res_model, attachment.res_id)
        # if not vals.get('res_model') or not vals.get('res_id'):
        #     raise UserError('Please choice the model/object to attach file.')
        return super(AccountDocuments, self).create(vals)

    @api.multi
    def write(self, vals):
        for record in self:
            if 'attachment_journal_id' not in vals and not record.attachment_journal_id:
                attachment_journal_id = self.env['ir.attachment.journal'].search([('company_id', '=', record.company_id.id),
                                                                                  ('journal_type', '=', 'documents')],
                                                                                limit=1)
                if attachment_journal_id:
                    vals['attachment_journal_id'] = attachment_journal_id.id
                else:
                    raise UserWarning("I can't find a journal of accounting documents. Probably deleted from the "
                                      "system...")

        if vals.get('ref', _('New')) == _('New') and 'attachment_journal_id' in vals:
            if 'company_id' in vals:
                vals['ref'] = self.env['ir.sequence'].with_context(
                    force_company=vals['company_id']).next_by_code('ir.attachment.datasheet') or _('New')
            else:
                vals['ref'] = self.env['ir.sequence'].next_by_code('ir.attachment.datasheet') or _('New')

        if 'object_id' in vals:
            vals['res_model'], vals['res_id'] = tuple(vals['object_id'].split(','))
            vals['res_id'] = int(vals['res_id'])
        if 'object_id' not in vals and 'res_model' in vals and 'res_id' in vals:
            vals['object_id'] = "%s,%s" % (vals['res_model'], vals['res_id'])
        _logger.info("OBJECT %s" % vals)
        return super(AccountDocuments, self).write(vals)

    @api.onchange('object_id')
    def _onchange_object_id(self):
        for doc in self:
            if doc.object_id:
                doc.res_model = doc.object_id._name
                doc.res_id = doc.object_id.id
                # _logger.info("OBJECT %s:%s(%s)" % (doc.object_id, doc.res_model, doc.res_id))
            elif doc.res_model and doc.res_id and not doc.object_id:
                doc.object_id = "%s,%s" % (doc.res_model, doc.res_id)

    @api.onchange('document_type_id', 'categ_id', 'datas')
    def _onchange_name(self):
        for record in self:
            # _logger.info("UPDATE %s:%s:%s:%s" % (record.document_type_id, record.categ_id, record.document_type_id,
            # record.attachment_journal_id))
            if record.document_type_id and record.categ_id and record.attachment_journal_id and not record.name:
                try:
                    name = safe_eval(record.attachment_journal_id.attachment_name, {'object': record, 'time': time})
                    if name.rfind('.') >= 0:
                        name, ext = name.rsplit('.', 1)
                    else:
                        ext = ''
                    name = "%s%s" % (name.strip(), ".%s" % ext)
                    record.name = name
                except ValueError:
                    _logger.info("Cannot adapt name...")


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _postprocess_pdf_report(self, attachment_name, attachment_file, buffer, record):
        res = super(IrActionsReport, self)._postprocess_pdf_report(attachment_name, attachment_file, buffer, record)
        object = self.env[self.model].browse(record.id)
        if 'company_id' in object._fields:
            company_id = object.company_id
            attachment_journal = self.env['ir.attachment.journal'].search([('company_id', '=', company_id.id),
                                                                           ('journal_type', '=', 'documents')],
                                                                          limit=1)
        else:
            attachment_journal = self.env['ir.attachment.journal'].search([('journal_type', '=', 'documents')],
                                                                          limit=1)
        if attachment_journal and attachment_journal.attachment_name and attachment_journal.attachment_file:
            attachment_name = safe_eval(attachment_journal.attachment_name, {'object': record, 'time': time})
            if attachment_name.rfind('.') >= 0:
                attachment_name, ext = attachment_name.rsplit('.', 1)
            else:
                ext = ''
            attachment_name = "%s%s" % (attachment_name.strip(), ".%s" % ext)
            attachment_file = safe_eval(attachment_journal.attachment_file, {'object': record, 'time': time})
            if attachment_file.rfind('.') >= 0:
                attachment_file, ext = attachment_file.rsplit('.', 1)
            else:
                ext = ''
            attachment_file = "%s%s" % (attachment_file.strip(), ".%s" % ext)
            _logger.info("NAME %s" % attachment_name)
            res.update({
                'attachment_name': attachment_name,
                'attachment_file': attachment_file,
            })
        return res

# class IrAttachment(models.Model):
#     _inherit = 'ir.attachment'
