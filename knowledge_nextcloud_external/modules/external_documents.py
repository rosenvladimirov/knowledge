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
        _logger.info("NEW DOCUMENT %s" % vals)
        if 'attachment_path_complete' in vals:
            return super(ExternalDocuments, self).\
                with_context(dict(self._context, attachment_nextcloud_path_complete=vals['attachment_path_complete'])).\
                create(vals)
        return super(ExternalDocuments, self).create(vals)

