# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _


class KnowledgeCrossAccount(models.TransientModel):
    _name = "knowledge.cross.account"
    _description = "Holder for cross variables when create clued attachment"

    def _get_domain_type(self):
        return [('display', '=', True)]

    # account documents
    document_type_id = fields.Many2one('account.documents.type', 'Type of document', domain=_get_domain_type)
    force_add_document = fields.Boolean('Force add account document')

    # product datasheets
    version = fields.Char('Version')
    manufacturer_id = fields.Many2one('product.manufacturer', string='Product Manufacturer')
    manufacturer_ids = fields.Many2many('product.manufacturer', string='Products Manufacturer')
    manufacturer = fields.Many2one('res.partner', string='Manufacturer', related="manufacturer_id.manufacturer", store=True)
    product_brand_id = fields.Many2one('product.brand', string='Brand', help='Select a brand for this product')
    product_tmpl_id = fields.Many2one('product.template', 'Product Template')
    iso_number = fields.Char('Certificate Number')
    date_issue = fields.Date('Issue Date')
    date_expiry = fields.Date('Expiry Date')
    notified_body_id = fields.Many2one('res.partner', 'Notified Body')
    qc_manager_id = fields.Many2one('res.users', 'QC Manager',
                                    help='The internal user that is resposnsible for Quality Control.')
    is_date = fields.Boolean('Has Expiry Date')
    force_add_datasheet = fields.Boolean('Force add datasheet')

    # external documents
    use_leads = fields.Boolean('Lead')
    lead_name = fields.Char('Lead name')
    force_add_external = fields.Boolean('Force add external document')
