# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.api import Environment, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = Environment(cr, SUPERUSER_ID, {})
    for record in env['account.documents'].search([('object_id', '=', False)]):
        _logger.info("RECORD %s" % record.name)
        if not record.res_model == 'account.invoice.protocol':
            record.write({'res_model': record.res_model, 'res_id': record.res_id})
