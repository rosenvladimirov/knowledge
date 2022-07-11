# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AttachmentStage(models.Model):
    _name = 'attachment.stage'
    _description = 'Attachment Stages'
    _order = 'sequence'

    name = fields.Char(string="Stage Name", required=True)
    description = fields.Text(string="Description", required=False)
    sequence = fields.Integer(string="Sequence", default="1", required=False)
    fold = fields.Boolean(string="Is Folded", required=False,
                          help="This stage is folded in the kanban view by default.")

    @api.multi
    def unlink(self):
        for record in self:
            if record.id == self.env.ref("knowledge.knowledge_system_state_draft").id or \
                record.id == self.env.ref("knowledge.knowledge_system_state_archived").id or \
                record.id == self.env.ref("knowledge.knowledge_system_state_active").id or \
                record.id == self.env.ref("knowledge.knowledge_system_state_cancelled").id:
                raise UserError(_('You cannot remove a system stage. '))
        return super(AttachmentStage, self).unlink()
