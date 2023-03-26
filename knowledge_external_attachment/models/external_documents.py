# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import os
import time

from odoo import api, fields, models, tools, _
# from odoo.addons.account.models.account_invoice import TYPE2REFUND
from odoo.exceptions import Warning as UserWarning, UserError
from odoo.tools.safe_eval import safe_eval

import logging

_logger = logging.getLogger(__name__)


class ExternalDocuments(models.Model):
    _inherit = "external.documents"

    attachment_root_path = fields.Char('Root path')
    attachment_path = fields.Char('Path')

    def _get_default_attachment_journal_id(self):
        if self._context.get('default_attachment_journal_id'):
            return self._context['default_attachment_journal_id']
        else:
            return self.env['ir.attachment.journal'].search([('company_id', '=', self.env.user.company_id.id),
                                                             ('journal_type', '=', 'external')], limit=1)

    def _get_domain_type(self):
        return [('display', '=', True)]

    @api.multi
    def _links_get(self):
        link_obj = self.env['res.request.link']
        return [(r.object, r.name) for r in link_obj.search([('object', 'in', ['sale.order', 'purchase.order',
                                                                               'stock.picking', 'account.invoice',
                                                                               'account.bank.statement',
                                                                               ])])]
                                                                               # 'crm.lead'])])]

    attachment_journal_id = fields.Many2one('ir.attachment.journal', string='Attachment Journal', required=True,
                                            ondelete='cascade', default=_get_default_attachment_journal_id)
    object_id = fields.Reference(string='Reference object', selection=_links_get, )
    # use_leads = fields.Boolean('Lead')
    # lead_name = fields.Char('Lead name')

    @api.model
    def create(self, vals):
        # lead_id = False
        attachment_journal_id = False
        if 'attachment_journal_id' not in vals:
            if self._context.get('attachment_journal'):
                attachment_journal_id = self.env['ir.attachment.journal'].browse(self._context['attachment_journal'])
            elif 'company_id' in vals:
                attachment_journal_id = self.env['ir.attachment.journal'].search(
                    [('company_id', '=', vals['company_id']),
                     ('journal_type', '=', 'external')],
                    limit=1)
            else:
                attachment_journal_id = self.env['ir.attachment.journal'].search([('journal_type', '=', 'external')],
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

        # force attach to partner
        if not self._context.get('block_res') and vals.get('partner_id') and not vals.get('res_model') and not vals.get('res_id'):
            vals['res_model'], vals['res_id'] = ('res.partner', vals['partner_id'])

        if vals.get('ir_attachment_id') and not vals.get('object_id'):
            attachment = self.env['ir.attachment'].browse(vals['ir_attachment_id'])
            if attachment:
                vals['object_id'] = "%s,%s" % (attachment.res_model, attachment.res_id)

        if attachment_journal_id:
            res = self.new(vals)
            name_formal = ''
            root_name_formal = ''
            if attachment_journal_id.attachment_path:
                try:
                    name_formal = safe_eval(attachment_journal_id.attachment_path, {'object': res, 'time': time})
                    _logger.info("LEGAL NAME %s" % name_formal)
                except UserError as error:
                    _logger.info("LEGAL NAME ERROR %s" % error.name)
                    _logger.debug("Traceback:", exc_info=True)
                    name_formal = vals.get('name')

            if attachment_journal_id.attachment_root_path:
                try:
                    root_name_formal = safe_eval(attachment_journal_id.attachment_root_path,
                                                 {'object': res, 'time': time})
                    _logger.info("LEGAL NAME %s" % root_name_formal)
                except UserError as error:
                    _logger.info("LEGAL NAME ERROR %s" % error.name)
                    _logger.debug("Traceback:", exc_info=True)
                    root_name_formal = ''

            if root_name_formal:
                vals['attachment_root_path'] = root_name_formal
                vals['attachment_path'] = name_formal
                vals['attachment_path_complete'] = os.path.join(root_name_formal, name_formal)

        return super(ExternalDocuments, self).create(vals)

    @api.multi
    def write(self, vals):
        for record in self:
            # lead_id = False
            if 'attachment_journal_id' not in vals and not record.attachment_journal_id:
                attachment_journal_id = self.env['ir.attachment.journal'].search([('company_id', '=', record.company_id.id),
                                                                                  ('journal_type', '=', 'external')],
                                                                                 limit=1)
                if attachment_journal_id:
                    vals['attachment_journal_id'] = attachment_journal_id.id
                else:
                    raise UserWarning("I can't find a journal of accounting documents. Probably deleted from the "
                                      "system...")
            # if vals.get('use_leads') and (vals.get('partner_id') or record.partner_id):
            #     # partner = self.env['res.partner'].browse(vals['partner_id'])
            #     name = (vals.get('lead_name') or record.lead_name) or (vals.get('name') or record.name)
            #     partner_id = vals.get('partner_id') or record.partner_id.id
            #     lead_id = self.env['crm.lead'].create({
            #         'name': name,
            #         'partner_id': partner_id,
            #     })
            #     vals['object_id'] = "%s,%s" % ('crm.lead', lead_id.id)
        if vals.get('ref', _('New')) == _('New') and 'attachment_journal_id' in vals:
            if 'company_id' in vals:
                vals['ref'] = self.env['ir.sequence'].with_context(
                    force_company=vals['company_id']).next_by_code('ir.attachment.datasheet') or _('New')
            else:
                vals['ref'] = self.env['ir.sequence'].next_by_code('ir.attachment.datasheet') or _('New')
        # force attach to partner
        if not self._context.get('block_res') and vals.get('partner_id') and (not vals.get('res_model') or record.res_model) and (not vals.get('res_id') or record.res_id):
            vals['res_model'], vals['res_id'] = ('res.partner', vals['partner_id'])
        # if lead_id:
        #     lead_id.message_post_with_view(
        #         'mail.message_origin_link',
        #         values={'self': record, 'origin': record},
        #         subtype_id=self.env.ref('mail.mt_note').id)
        return super(ExternalDocuments, self).write(vals)


    @api.onchange('categ_id', 'datas')
    def _onchange_name(self):
        for record in self:
            # _logger.info("UPDATE %s:%s:%s:%s" % (record.document_type_id, record.categ_id, record.document_type_id, record.attachment_journal_id))
            if record.categ_id and record.attachment_journal_id and not record.name:
                try:
                    record.name = safe_eval(record.attachment_journal_id.attachment_name, {'object': record, 'time': time})
                except ValueError:
                    _logger.info("Cannot adapt name...")
