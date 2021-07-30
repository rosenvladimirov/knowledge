# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
import logging

_logger = logging.getLogger(__name__)


class KnowledgeCrossDatasheets(models.TransientModel):
    _name = "knowledge.cross.datasheets"
    _description = "Holder for cross variables when create clued attachment"

    @api.multi
    def _links_get(self):
        link_obj = self.env['res.request.link']
        return [(r.object, r.name) for r in link_obj.search([('object', 'in', ['sale.order', 'purchase.order',
                                                                               'stock.picking', 'account.invoice',
                                                                               'account.bank.statement',
                                                                               'crm.lead'])])]

    ir_attachment_id = fields.Many2one('ir.attachment', string='Related attachment', required=True)
    object_id = fields.Reference(string='Reference object', selection=_links_get, )
    partner_id = fields.Many2one('res.partner', 'Partner')

    # product datasheets
    version = fields.Char('Version')
    manufacturer_id = fields.Many2one('product.manufacturer', string='Product Manufacturer')
    manufacturer_ids = fields.Many2many('product.manufacturer', string='Products Manufacturer')
    manufacturer = fields.Many2one('res.partner', string='Manufacturer', related="manufacturer_id.manufacturer",
                                   store=True)
    product_brand_id = fields.Many2one('product.brand', string='Brand', help='Select a brand for this product')
    product_tmpl_id = fields.Many2one('product.template', 'Product Template')
    product_id = fields.Many2one('product.product', 'Product Variant')
    iso_number = fields.Char('Certificate Number')
    date_issue = fields.Date('Issue Date')
    date_expiry = fields.Date('Expiry Date')
    notified_body_id = fields.Many2one('res.partner', 'Notified Body')
    qc_manager_id = fields.Many2one('res.users', 'QC Manager',
                                    help='The internal user that is resposnsible for Quality Control.')
    is_date = fields.Boolean('Has Expiry Date')
    force_add_datasheet = fields.Boolean('Force add datasheet')

    @api.model
    def default_get(self, fields_list):
        res = super(KnowledgeCrossDatasheets, self).default_get(fields_list)
        external_document = self.env['external.documents'].browse(self._context.get('default_external_document_id'))
        res.update({
            'ir_attachment_id': external_document.ir_attachment_id and external_document.ir_attachment_id.id or False,
            'object_id': external_document.object_id and "%s,%s" % tuple([external_document.object_id._name, external_document.object_id.id]) or False,
            'partner_id': external_document.partner_id and external_document.partner_id.id or False,
        })
        return res

    @api.multi
    def add_new_datasheet(self):
        for record in self:
            docs = self.env['product.manufacturer.datasheets'].search(
                [('ir_attachment_id', '=', record.ir_attachment_id.id)])
            if not docs or record.force_add_datasheet \
                and not (record.ir_attachment_id.res_model == 'res.partner'
                         and record.ir_attachment_id.res_id == record.partner_id.id):
                values = {
                    'ir_attachment_id': record.ir_attachment_id.id,
                    'object_id': record.object_id and "%s,%s" % (record.object_id._name, record.object_id.id) or False,
                    'version': record.version,
                    'manufacturer_id': record.manufacturer_id.id,
                    'manufacturer_ids': record.manufacturer_ids.ids,
                    'manufacturer': record.manufacturer.id,
                    'product_tmpl_id': record.product_tmpl_id.id,
                    'iso_number': record.iso_number,
                    'date_issue': record.date_issue,
                    'date_expiry': record.date_expiry,
                    'notified_body_id': record.notified_body_id.id,
                    'qc_manager_id': record.qc_manager_id.id,
                    'is_date': record.is_date,
                }
                if record.product_brand_id:
                    values.update({
                        'res_model': record.product_brand_id._name,
                        'res_id': record.product_brand_id.id,
                    })
                elif record.product_id:
                    values.update({
                        'res_model': record.product_id._name,
                        'res_id': record.product_id.id,
                    })
                else:
                    values.update({
                        'res_model': record.partner_id._name,
                        'res_id': record.partner_id.id,
                    })
                res = docs.with_context(dict(self._context, block_res=True)).create(values)
                if res:
                    record.write({
                        'object_id': "%s,%s" % (res.object_id._name, res.object_id.id)
                    })
        return False
