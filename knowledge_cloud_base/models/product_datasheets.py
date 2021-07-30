# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

import logging

_logger = logging.getLogger(__name__)


class ProductManufacturerDatasheets(models.Model):
    _inherit = 'product.manufacturer.datasheets'

    object_date = fields.Date("Object date", compute="_compute_object_date")
    object_env = fields.Char("Object environment", compute="_compute_object_env")

    @api.multi
    def _compute_object_date(self):
        for record in self:
            if record.object_id:
                record.object_date = record.object_id.create_date
            else:
                record.object_date = fields.Date.today()

    @api.multi
    def _compute_object_env(self):
        for record in self:
            if record.object_id:
                if record.object_id._name == 'product.product':
                    if record.object_id.manufacturer_id and record.object_id.product_brand_id and record.object_id.product_brand_id.partner_id:
                        if record.object_id.manufacturer_id != record.object_id.product_brand_id.partner_id:
                            record.object_env = "{partner}/{brand}/{manufacturer}".format(partner=record.object_id.product_brand_id.partner_id.name,
                                                                                          brand=record.object_id.product_brand_id.name,
                                                                                          manufacturer=record.object_id.manufacturer_id.name)
                        else:
                            record.object_env = "{manufacturer}/{brand}".format(manufacturer=record.object_id.manufacturer_id.name,
                                                                                brand=record.object_id.product_brand_id.name)
                    elif record.object_id.manufacturer_id and not record.object_id.product_brand_id:
                        record.object_env = "{manufacturer}".format(manufacturer=record.object_id.manufacturer_id.name)
                    elif not record.object_id.manufacturer_id and record.object_id.product_brand_id and record.object_id.product_brand_id.partner_id:
                        record.object_env = "{partner}/{brand}".format(partner=record.object_id.product_brand_id.partner_id.name,
                                                                       brand=record.object_id.product_brand_id.name)
                    else:
                        record.object_env = "{template}/{product}".format(template=record.object_id.product.product_tmpl_id.name, product=record.object_id.name)

                elif record.object_id._name == 'product.template':
                    if record.object_id.manufacturer_id and record.object_id.product_brand_id and record.object_id.product_brand_id.partner_id:
                        if record.object_id.manufacturer_id != record.object_id.product_brand_id.partner_id:
                            record.object_env = "{partner}/{brand}/{manufacturer}".format(partner=record.object_id.product_brand_id.partner_id.name,
                                                                                          brand=record.object_id.product_brand_id.name,
                                                                                          manufacturer=record.object_id.manufacturer_id.name)
                        else:
                            record.object_env = "{manufacturer}/{brand}".format(manufacturer=record.object_id.manufacturer_id.name,
                                                                                brand=record.object_id.product_brand_id.name)
                    elif record.object_id.manufacturer_id and not record.object_id.product_brand_id:
                        record.object_env = "{manufacturer}".format(manufacturer=record.object_id.manufacturer_id.name)
                    elif not record.object_id.manufacturer_id and record.object_id.product_brand_id and record.object_id.product_brand_id.partner_id:
                        record.object_env = "{partner}/{brand}".format(partner=record.object_id.product_brand_id.partner_id.name,
                                                                       brand=record.object_id.product_brand_id.name)
                    else:
                        record.object_env = "{template}".format(template=record.object_id.name)

                elif record.object_id._name == 'product.brand':
                    if record.object_id.product_brand_id and record.object_id.product_brand_id.partner_id:
                        record.object_env = "{partner}/{brand}".format(partner=record.object_id.product_brand_id.partner_id.name,
                                                                       brand=record.object_id.product_brand_id.name)
                    else:
                        record.object_env = "{brand}".format(brand=record.object_id.product_brand_id.name)
                else:
                    record.object_env = 'Unknown'
            else:
                record.object_env = 'Unknown'

    @api.multi
    def restore_attachment_from_cloud(self):
        return self.ir_attachment_id._restore_attachment_from_cloud()

    @api.multi
    def share_attachment_from_cloud(self):
        # att = self.env['external.documents'].browse(self._context['default_external_document_id'])
        _logger.info("INVOKE SHARE %s:%s" % (self.ir_attachment_id, self))
        return self.ir_attachment_id._share_file_with_link()

    @api.multi
    def _filter_non_synced_attachments(self):
        return self.ir_attachment_id._filter_non_synced_attachments()

