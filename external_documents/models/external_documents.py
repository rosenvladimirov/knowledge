# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
#from odoo.addons.account.models.account_invoice import TYPE2REFUND

import logging
_logger = logging.getLogger(__name__)


class ExternlDocuments(models.Model):
    _name = "external.documents"
    _description = "Collection of all scaned and copy of original documents linked with partners."
    _inherits = {'ir.attachment': 'ir_attachment_id',}
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ir_attachment_id = fields.Many2one('ir.attachment', string='Related attachment', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', 'Partner')
    contact_partner_id = fields.Many2one('res.partner', 'Contact person partner')
    document_type_id = fields.Many2one('external.documents.type', 'Type of document')
    color = fields.Integer(string="Color")
    responsible_user_ids = fields.Many2many('res.users', string='Responsible users')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for record in self:
            if record.partner_id and not record.res_model and not record.res_id:
                record.res_model, record.res_id = ('res.partner', record.partner_id.id)

    @api.model
    def search_documents_for_partner(self, att):
        partners = set([])
        # check for partner_id
        if 'partner_id' in att._fields:
            partners.update([att.partner_id])
        # check for owner_id
        # if 'owner_id' in att._fields:
        #     partners.append(att.owner_id)
        # check for location owner
        if att._name == 'stock.picking':
            for line in att.move_line_ids:
                if line.owner_id:
                    partners.update([line.owner_id])
                if line.location_id.partner_id:
                    partners.update([line.location_id.partner_id])
                if line.location_dest_id.partner_id:
                    partners.update([line.location_dest_id.partner_id])
        if att._name == 'account.bank.statement':
            for line in att.line_ids:
                if line.partner_id:
                    partners.update([line.partner_id])
        return partners

    @api.model
    def create(self, vals):
        res = super(ExternlDocuments, self).create(vals)
        if vals.get('responsible_user_ids') or vals.get('contact_partner_id'):
            for x in res.responsible_user_ids:
                if x.partner_id.id not in res.message_partner_ids.ids:
                    res.message_subscribe([x.partner_id.id])
            if res.contact_partner_id and res.contact_partner_id.id not in res.message_partner_ids.ids:
                res.message_subscribe([res.contact_partner_id.id])
        return res

    @api.multi
    def write(self, values):
        res = super(ExternlDocuments, self).write(values)
        for record in self:
            if values.get('responsible_user_ids') or values.get('contact_partner_id'):
                for x in record.responsible_user_ids:
                    if x.partner_id.id not in record.message_partner_ids.ids:
                        record.message_subscribe([x.partner_id.id])
                if record.contact_partner_id and record.contact_partner_id.id not in record.message_partner_ids.ids:
                    record.message_subscribe([record.contact_partner_id.id])
    #     return res

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        res = {}
        if self.partner_id:
            if self.partner_id.is_company:
                if self.partner_id.child_ids:
                    ids = set([])
                    partners = self.partner_id.mapped('child_ids')
                    for partner in partners:
                        if partner.contact_type == 'standalone' and not partner.contact_id:
                            ids.update(partner.ids)
                        elif partner.contact_type == 'attached':
                            ids.update(partner.contact_id.ids)
                    ids = list(ids)
                    res.update({'domain': {'partner_contact_id': [('customer', '=', True), ('id', 'in', ids)]}})
                else:
                    res.update({'domain': {'partner_contact_id': []}})
            else:
                res.update({'domain': {'partner_contact_id': []}})
        return res


# class IrActionsReport(models.Model):
#     _inherit = 'ir.actions.report'
#
#     @api.multi
#     def postprocess_pdf_report(self, record, buffer):
#         attachment = super(IrActionsReport, self).postprocess_pdf_report(record, buffer)
#         if attachment:
#             docs = self.env['external.documents'].search([('ir_attachment_id', '=', attachment.id)])
#             if not docs:
#                 ctx = self._context.copy()
#                 att = self.env[attachment.res_model].browse(attachment.res_id)
#
#                 partners = self.env['external.documents'].search_documents_for_partner(att)
#                 values = {'ir_attachment_id': attachment.id}
#                 if 'company_id' in att._fields:
#                     values.update({
#                         'company_id': att.company_id.id,
#                     })
#                 # _logger.info("ATTACHMENT %s:(%s)%s:%s" % (att.partner_id, attachment, attachment.res_model, attachment.res_id))
#                 if partners:
#                     ctx.update({'block_res': True})
#                     for partner in list(partners):
#                         values.update({'partner_id': partner.id})
#                         docs.with_context(ctx).create(values)
#                         _logger.info("EXTERNAL %s(%s)" % (docs, values))
#                 else:
#                     docs.create(values)
#         return attachment


class ExternalDocumentsType(models.Model):
    _name = "external.documents.type"
    _description = "Global nomenclature for external documents."

    active = fields.Boolean('Active', default=True,
            help="If the active field is set to False, it will allow you to hide the Type documents without removing it.")
    name = fields.Char('Name', translate=True)
    code = fields.Char('Code')
