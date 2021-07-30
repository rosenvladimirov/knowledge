# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def _make_cloud_files(self, folder_id, res_model, res_id, attachments=None, sync_model_id=False):
        if attachments is None and 'ir_attachment_id' in self.env[res_model]._fields:
            real_attachment = self.env[res_model].browse(res_id).ir_attachment_id
            # _logger.info("ATTACHMENT %s(%s:%s:%s)" % (real_attachment, real_attachment.name, real_attachment.res_model, real_attachment.res_id))
            if real_attachment.res_model and real_attachment.res_id:
                res_model, res_id = real_attachment.res_model, real_attachment.res_id
        if attachments is not None and 'ir_attachment_id' in attachments._fields:
            real_attachment = attachments.ir_attachment_id
            # _logger.info("ATTACHMENT %s(%s:%s:%s)" % (real_attachment, real_attachment.name, real_attachment.res_model, real_attachment.res_id))
            if real_attachment.res_model and real_attachment.res_id:
                res_model, res_id = real_attachment.res_model, real_attachment.res_id
        return super(IrAttachment, self)._make_cloud_files(folder_id, res_model, res_id, attachments=attachments, sync_model_id=sync_model_id)
