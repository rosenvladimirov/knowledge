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

    object_date = fields.Date("Object date", compute="_compute_object_date")
    object_env = fields.Char("Object environment", compute="_compute_object_env")

    @api.multi
    def _compute_object_date(self):
        for record in self:
            if record.object_id:
                if record.object_id._name == 'sale.order':
                    record.object_date = record.object_id.date_order
                elif record.object_id._name == 'account.invoice':
                    record.object_date = record.object_id.date_invoice
                elif record.object_id._name == 'purchase.order':
                    record.object_date = record.object_id.date_order
                elif record.object_id._name == 'stock.picking':
                    record.object_date = record.object_id.date_done
                elif record.object_id._name == 'account.bank.statement':
                    record.object_date = record.object_id.date
                else:
                    record.object_date = record.object_id.create_date
            else:
                record.object_date = fields.Date.today()

    @api.multi
    def _compute_object_env(self):
        for record in self:
            if record.object_id:
                if record.object_id._name == 'sale.order':
                    record.object_env = record.object_id.name
                elif record.object_id._name == 'account.invoice':
                    purchase_order = record.object_id.purchase_id
                    sale_orders = record.object_id.mapped('invoice_line_ids').mapped('sale_line_ids').mapped('order_id')
                    if len(sale_orders.ids) > 0:
                        record.object_env = '-'.join([x.name for x in sale_orders])
                    elif len(purchase_order.ids) > 0:
                        record.object_env = purchase_order.name
                    else:
                        record.object_env = record.object_id.display_name
                elif record.object_id._name == 'purchase.order':
                    record.object_env = record.object_id.name
                elif record.object_id._name == 'stock.picking':
                    sale = record.object_id.sale_id
                    purchase = record.object_id.purchase_id
                    if len(sale.ids):
                        record.object_env = record.object_id.sale_id.name
                    elif len(purchase.ids) > 0:
                        record.object_env = record.object_id.purchase_id.name
                    else:
                        record.object_env = record.object_id.name
                elif record.object_id._name == 'account.bank.statement':
                    record.object_env = record.object_id.name
                else:
                    record.object_env = record.categ_id and record.categ_id.name or 'Unknown'
            else:
                record.object_env = record.categ_id and record.categ_id.name or 'Unknown'

    @api.multi
    def restore_attachment_from_cloud(self):
        return self.ir_attachment_id._restore_attachment_from_cloud()

    @api.multi
    def share_attachment_from_cloud(self):
        # _logger.info("INVOKE SHARE %s:%s" % (self.ir_attachment_id, self))
        return self.ir_attachment_id._share_file_with_link()

    @api.multi
    def un_share_attachment_from_cloud(self):
        _logger.info("INVOKE UN SHARE %s:%s" % (self.ir_attachment_id, self))
        return self.ir_attachment_id._delete_share()

    @api.multi
    def _filter_non_synced_attachments(self):
        return self.ir_attachment_id._filter_non_synced_attachments()

