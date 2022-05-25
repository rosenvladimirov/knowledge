# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _, fields


class IrAttachmentJournalTemplate(models.Model):
    _inherit = "ir.attachment.journal.template"

    journal_type = fields.Selection(selection_add=[('mrp', _('MRP technical Documents')),])


class IrAttachmentJournal(models.Model):
    _inherit = "ir.attachment.journal"

    journal_type = fields.Selection(selection_add=[('mrp', _('MRP technical Documents')),])

    def _open_action(self):
        action_name = super(IrAttachmentJournal, self)._open_action()
        if self.res_model == 'mrp.technical.documents':
            return "mrp_external_docs.knowledge_action_mrp_technical_documents"
        return action_name

    @api.multi
    def get_journal_dashboard_datas(self):
        res = super(IrAttachmentJournal, self).get_journal_dashboard_datas()
        title = res.get('title', '')
        if self.res_model == 'mrp.technical.documents':
            title = "MRP technical documents"
        return {'title': title}
