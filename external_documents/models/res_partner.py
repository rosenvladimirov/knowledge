# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    documents_count = fields.Integer(compute="_get_count_documets")

    def _get_documents_context(self):
        return "{'default_res_model': '%s','default_res_id': %d}" % ('res.partner', self.id)

    def _get_documents_domain(self):
        return ['|']

    @api.multi
    def _get_count_documets(self):
        for partner in self:
            domain = partner._get_documents_domain()
            domain += [
                '&', ('res_model', '=', 'res.partner'), ('res_id', '=', partner.id),
                ('partner_id', '=', partner.id), ]
            partner.documents_count = self.env['external.documents'].search_count(domain)

    @api.multi
    def action_see_documents(self):
        for partner in self:
            domain = partner._get_documents_domain()
            domain += [
                '&', ('res_model', '=', 'res.partner'), ('res_id', '=', partner.id),
                ('partner_id', '=', partner.id),
            ]

            attachment_view = self.env.ref('external_documents.view_documents_file_kanban_external')
            return {
                'name': _('Documents'),
                'domain': domain,
                'res_model': 'external.documents',
                'type': 'ir.actions.act_window',
                'view_id': attachment_view.id,
                'views': [(attachment_view.id, 'kanban'), (False, 'form')],
                'view_mode': 'kanban,tree,form',
                'view_type': 'form',
                'help': _('''<p class="oe_view_nocontent_create">
                            Click to upload document to your invoice.
                        </p><p>
                            Use this feature to store any files, like original invoices.
                        </p>'''),
                'limit': 80,
                'context': partner._get_documents_context()
            }
        return False
