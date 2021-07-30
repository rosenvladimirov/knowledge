# -*- coding: utf-8 -*-

import time

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval

import logging
_logger = logging.getLogger(__name__)


class sync_model(models.Model):
    _inherit = "sync.model"

    @api.model
    def _return_folder_name(self):
        record_id = self.env[self.model].search([('company_id', '=', self.company_id.id)], limit=1)
        _logger.info("MODEL NAME GET %s" % record_id)
        if 'attachment_journal_id' in record_id._fields and record_id.attachment_journal_id and record_id.attachment_journal_id.attachment_root_path:
            try:
                name = safe_eval(record_id.attachment_journal_id.attachment_root_path,
                                        {'object': record_id, 'time': time})
                _logger.info("MODEL NAME %s:%s" % (record_id, name))
            except ValueError:
                return super(sync_model, self)._return_folder_name()
        else:
            return super(sync_model, self)._return_folder_name()
        return name
