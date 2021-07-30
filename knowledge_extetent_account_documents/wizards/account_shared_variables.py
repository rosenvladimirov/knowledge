# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

import logging
_logger = logging.getLogger(__name__)


class KnowledgeCrossAccounts(models.TransientModel):
    _name = "knowledge.cross.accounts"
    _description = "Holder for cross variables when create clued attachment"

    def _get_domain_type(self):
        return [('display', '=', True)]

    @api.multi
    def _links_get(self):
        link_obj = self.env['res.request.link']
        return [(r.object, r.name) for r in link_obj.search([('object', 'in', ['sale.order', 'purchase.order',
                                                                               'stock.picking', 'account.invoice',
                                                                               'account.bank.statement'])])]

    ir_attachment_id = fields.Many2one('ir.attachment', string='Related attachment', required=True)
    object_id = fields.Reference(string='Reference object', selection=_links_get, )
    # account documents
    document_type_id = fields.Many2one('account.documents.type', 'Type of document', domain=_get_domain_type)
    force_add_document = fields.Boolean('Force add account document')
    external_document_id = fields.Many2one('external.documents', 'External document')

    @api.model
    def default_get(self, fields_list):
        res = super(KnowledgeCrossAccounts, self).default_get(fields_list)
        external_document = self.env['external.documents'].browse(self._context.get('default_external_document_id'))
        res.update({
            'external_document_id': external_document.id,
            'ir_attachment_id': external_document.ir_attachment_id and external_document.ir_attachment_id.id or False,
            'object_id': external_document.object_id and "%s,%s" % tuple([external_document.object_id._name, external_document.object_id.id]) or False,
        })
        # _logger.info("CONTEXT %s-%s-%s" % (self._context, external_document, res))
        return res

    @api.multi
    def add_new_document(self):
        for record in self:
            if record.object_id:
                docs = self.env['account.documents'].search([('ir_attachment_id', '=', record.ir_attachment_id.id)])
                if not docs or record.force_add_document:
                    values = {
                        'ir_attachment_id': record.ir_attachment_id.id,
                        'res_model': record.object_id._name,
                        'res_id': record.object_id.id,
                        'object_id': "%s,%s" % (record.object_id._name, record.object_id.id),
                        'document_type_id': record.document_type_id.id,
                    }
                    res = docs.with_context(dict(self._context, block_res=True)).create(values)
                    if res:
                        record.external_document_id.write({
                            'object_id': "%s,%s" % (res.object_id._name, res.object_id.id)
                        })
        return False
