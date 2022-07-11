# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import os
import time

from odoo import api, fields, models, tools, _
# from odoo.addons.account.models.account_invoice import TYPE2REFUND
from odoo.exceptions import Warning as UserWarning, UserError
from odoo.tools.safe_eval import safe_eval

import logging

_logger = logging.getLogger(__name__)


class ExternalDocuments(models.Model):
    _inherit = "external.documents"

    @api.model
    def create(self, vals):
        if 'attachment_journal_id' in vals:
            res = self.new(vals)
            attachment_journal_id = self.env['ir.attachment.journal'].browse(vals['attachment_journal_id'])
            name_formal = ''
            root_name_formal = ''
            try:
                name_formal = safe_eval(attachment_journal_id.attachment_path,
                                        {'object': res, 'time': time})
                _logger.info("LEGAL NAME %s" % name_formal)
            except ValueError:
                _logger.info("LEGAL NAME ERROR %s" % ValueError)
                name_formal = ''
            try:
                root_name_formal = safe_eval(attachment_journal_id.attachment_root_path,
                                        {'object': res, 'time': time})
                _logger.info("LEGAL NAME %s" % root_name_formal)
            except ValueError:
                _logger.info("LEGAL NAME ERROR %s" % ValueError)
                root_name_formal = ''
            if name_formal:
                name_formal = os.path.join(root_name_formal, name_formal, vals['datas_fname'])
                return super(ExternalDocuments, self).\
                    with_context(dict(self._context, attachment_nextcloud_path_complete=name_formal))\
                    .create(vals)
        return super(ExternalDocuments, self).create(vals)
