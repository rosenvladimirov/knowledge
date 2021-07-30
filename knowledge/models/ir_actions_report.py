# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import time

from odoo import api, models, _
from odoo.exceptions import AccessError
from odoo.tools.safe_eval import safe_eval
from odoo.addons.base.ir.ir_actions_report import IrActionsReport as iractionsreport

import logging

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _postprocess_pdf_report(self, attachment_name, attachment_file, buffer, record):
        return {
            'name': attachment_name,
            'datas': base64.encodestring(buffer.getvalue()),
            'datas_fname': attachment_file,
            'res_model': self.model,
            'res_id': record.id,
        }

    @api.multi
    def postprocess_pdf_report(self, record, buffer):
        '''Hook to handle post processing during the pdf report generation.
        The basic behavior consists to create a new attachment containing the pdf
        base64 encoded.

        :param record_id: The record that will own the attachment.
        :param pdf_content: The optional name content of the file to avoid reading both times.
        :return: The newly generated attachment if no AccessError, else None.
        '''
        attachment_file = attachment_name = safe_eval(self.attachment, {'object': record, 'time': time})
        if not attachment_name:
            return None
        attachment_vals = self._postprocess_pdf_report(attachment_name, attachment_file, buffer, record)
        attachment = None
        try:
            attachment = self.env['ir.attachment'].create(attachment_vals)
        except AccessError:
            _logger.info("Cannot save PDF report %r as attachment", attachment_vals['name'])
        else:
            _logger.info('The PDF document %s is now saved in the database', attachment_vals['name'])
        return attachment


iractionsreport.postprocess_pdf_report = IrActionsReport.postprocess_pdf_report
