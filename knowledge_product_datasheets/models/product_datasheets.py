# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
#from odoo.addons.account.models.account_invoice import TYPE2REFUND
from odoo.exceptions import Warning as UserWarning

import logging
_logger = logging.getLogger(__name__)


class ProductManufacturerDatasheets(models.Model):
    _inherit = "product.manufacturer.datasheets"

    def _get_default_attachment_journal_id(self):
        if self._context.get('default_attachment_journal_id'):
            return self._context['default_attachment_journal_id']
        else:
            return self.env['ir.attachment.journal'].search([('company_id', '=', self.env.user.company_id.id),
                                                             ('journal_type', '=', 'datasheets')], limit=1)

    def _get_domain_type(self):
        return [('display', '=', True)]

    @api.multi
    def _links_get(self):
        link_obj = self.env['res.request.link']
        return [(r.object, r.name) for r in link_obj.search([('object', 'in', ['product.product', 'product.template',
                                                                              'res.partner', 'product.brand'])])]

    attachment_journal_id = fields.Many2one('ir.attachment.journal', string='Attachment Journal', required=True,
                                            ondelete='cascade', default=_get_default_attachment_journal_id)
    object_id = fields.Reference(string='Reference object', selection=_links_get,)

    @api.model
    def create(self, vals):
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

        if vals.get('object_id') and (not vals.get('res_model') and not vals.get('res_id')):
            vals['res_model'], vals['res_id'] = tuple(vals['object_id'].split(','))
            vals['res_id'] = int(vals['res_id'])

        if not vals.get('object_id') and 'res_model' in vals and 'res_id' in vals:
            vals['object_id'] = "%s,%s" % (vals['res_model'], vals['res_id'])

        if 'ir_attachment_id' in vals and 'object_id' not in vals:
            attachment = self.env['ir.attachment'].browse(vals['ir_attachment_id'])
            if attachment:
                vals['object_id'] = "%s,%s" % (attachment.res_model, attachment.res_id)
        return super(ProductManufacturerDatasheets, self).create(vals)

    @api.multi
    def write(self, vals):
        for record in self:
            if 'attachment_journal_id' not in vals and not record.attachment_journal_id:
                attachment_journal_id = self.env['ir.attachment.journal'].search([('company_id', '=', record.company_id.id),
                                                                                  ('journal_type', '=', 'datasheets')],
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

        if vals.get('object_id') and (not vals.get('res_model') and not vals.get('res_id')):
            vals['res_model'], vals['res_id'] = tuple(vals['object_id'].split(','))
            vals['res_id'] = int(vals['res_id'])
        if not vals.get('object_id') and 'res_model' in vals and 'res_id' in vals:
            vals['object_id'] = "%s,%s" % (vals['res_model'], vals['res_id'])
        return super(ProductManufacturerDatasheets, self).write(vals)

    @api.onchange('object_id')
    def _onchange_object_id(self):
        for doc in self:
            if doc.object_id:
                doc.res_model = doc.object_id._name
                doc.res_id = doc.object_id.id
                # _logger.info("OBJECT %s:%s(%s)" % (doc.object_id, doc.res_model, doc.res_id))
            elif doc.res_model and doc.res_id:
                doc.object_id = "%s,%s" % (doc.res_model, doc.res_id)
