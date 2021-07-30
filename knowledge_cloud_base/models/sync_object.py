# -*- coding: utf-8 -*-

import time
import json

from odoo.tools.safe_eval import safe_eval
from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)


class sync_object(models.Model):
    _inherit = "sync.object"

    @api.model
    def _return_folder_name(self, res_model, res_id, sync_model_id, current_id):
        # legal_name = super(sync_object, self)._return_folder_name(res_model, res_id, sync_model_id, current_id)
        block_separate = False
        record_id = self.env[res_model].browse(res_id)
        _logger.info("OBJECT %s" % record_id)
        if 'attachment_journal_id' in record_id._fields and record_id.attachment_journal_id and record_id.attachment_journal_id.attachment_path:
            try:
                name_formal = safe_eval(record_id.attachment_journal_id.attachment_path, {'object': record_id, 'time': time})
                _logger.info("LEGAL NAME %s" % name_formal)
            except ValueError:
                _logger.info("LEGAL NAME ERROR %s" % ValueError)
                return super(sync_object, self)._return_folder_name(res_model, res_id, sync_model_id, current_id)
        else:
            return super(sync_object, self)._return_folder_name(res_model, res_id, sync_model_id, current_id)
        name_formal = self.env["ir.attachment"].with_context(dict(self._context, use_folder=True)).remove_illegal_characters(name_formal)
        legal_name = name_formal and name_formal or str(record_id.id)
        return legal_name

    # @api.model
    # def _unique_folder_name(self, legal_name, sync_model_id, current_id):
    #     name = super(sync_object, self)._unique_folder_name(legal_name, sync_model_id, current_id)
    #     _logger.info("UNIQUE %s=%s" % (legal_name, name))
    #     if legal_name != name:
    #         return False
    #     return name
