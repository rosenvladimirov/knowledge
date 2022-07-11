# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import io
import os
import base64
import shutil

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from odoo import fields, models, tools, api, _
from odoo.addons.document.models.ir_attachment import IrAttachment as irattachment
from odoo.addons.queue_job.job import job

import logging

_logger = logging.getLogger(__name__)

_img_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/src/img'))


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    # Used for Kanban grouped_by view
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['attachment.stage'].search([])
        return stage_ids

    def _default_stage_id(self):
        try:
            res = self.env.ref('knowledge.knowledge_system_state_draft')
        except ValueError:
            res = False
        return res

    # journal_name = fields.Char('Journal Attachment Name', required=True)
    # Add index to res_model because filtering on it is a common use case
    # attachment_journal_id = fields.Many2one('ir.attachment.journal', 'Attachment Journal')
    ref = fields.Char('Reference name', default=lambda self: _('New'))
    res_model = fields.Char(index=True)
    stage_id = fields.Many2one(
        'attachment.stage',
        string="Stage",
        group_expand='_read_group_stage_ids',
        help="Select the current stage of the attachment.",
        track_visibility='onchange',
        index=True,
        default=lambda self: self._default_stage_id(),
    )
    direction = fields.Selection([('none', _('No direction')),
                                  ('in', _('Incoming documents')),
                                  ('out', _('Оutgoing documents'))
                                  ], string="Movement of the documents", default="none")
    categ_id = fields.Many2one('ir.attachment.journal.category', 'Attachment category')
    # color = fields.Integer(string="Color")
    custom_thumbnail = fields.Binary(string="Custom Thumbnail")
    custom_thumbnail_medium = fields.Binary(string="Medium Custom Thumbnail")
    custom_thumbnail_small = fields.Binary(string="Small Custom Thumbnail")
    thumbnail = fields.Binary(compute='_compute_thumbnail', string="Thumbnail")
    thumbnail_medium = fields.Binary(compute='_compute_thumbnail_medium', string="Medium Thumbnail")
    thumbnail_small = fields.Binary(compute='_compute_thumbnail_small', string="Small Thumbnail")
    attachment_path_complete = fields.Char('Hard link path')

    @api.depends('custom_thumbnail')
    def _compute_thumbnail(self):
        for record in self:
            if record.custom_thumbnail:
                record.thumbnail = record.with_context({}).custom_thumbnail
            else:
                extension = record.mimetype.split("/")[1]
                if record.url:
                    extension = record.url.replace('http://', '').replace('https://', '').split("/")[0].split('.')[0]
                path = os.path.join(_img_path, "file_%s.png" % extension)
                if not os.path.isfile(path):
                    path = os.path.join(_img_path, "file_unkown.png")
                with open(path, "rb") as image_file:
                    record.thumbnail = base64.b64encode(image_file.read())

    @api.depends('custom_thumbnail_medium')
    def _compute_thumbnail_medium(self):
        for record in self:
            if record.custom_thumbnail_medium:
                record.thumbnail_medium = record.with_context({}).custom_thumbnail_medium
            else:
                extension = record.mimetype.split("/")[1]
                if record.url:
                    extension = record.url.replace('http://', '').replace('https://', '').split("/")[0].split('.')[0]
                path = os.path.join(_img_path, "file_%s_128x128.png" % extension)
                if not os.path.isfile(path):
                    path = os.path.join(_img_path, "file_unkown_128x128.png")
                with open(path, "rb") as image_file:
                    record.thumbnail_medium = base64.b64encode(image_file.read())

    @api.depends('custom_thumbnail_small')
    def _compute_thumbnail_small(self):
        for record in self:
            if record.custom_thumbnail_small:
                record.thumbnail_small = record.with_context({}).custom_thumbnail_small
            else:
                extension = record.mimetype.split("/")[1]
                if record.url:
                    extension = record.url.replace('http://', '').replace('https://', '').split("/")[0].split('.')[0]
                path = os.path.join(_img_path, "file_%s_64x64.png" % extension)
                if not os.path.isfile(path):
                    path = os.path.join(_img_path, "file_unkown_64x64.png")
                with open(path, "rb") as image_file:
                    record.thumbnail_small = base64.b64encode(image_file.read())

    @api.multi
    @job
    def _file_copy_write(self, fname):
        full_file_name = self._context['attachment_path_complete']
        for attachment in self:
            dir_name = os.path.dirname(full_file_name)
            if not os.path.isdir(dir_name):
                with tools.ignore(OSError):
                    os.makedirs(dir_name)
            try:
                shutil.copy(fname, full_file_name)
            except IOError:
                _logger.info("_file_copy_write writing %s", full_file_name, exc_info=True)
        return os.path.dirname(full_file_name), os.path.basename(full_file_name)

    @api.model
    def _file_write(self, value, checksum):
        if self._context.get('attachment_path_complete') and self._storage() == 'file':
            fname = super(IrAttachment, self)._file_write(value, checksum)
            dir_name, file_name = self.with_delay()._file_copy_write(fname)
            if dir_name:
                self.sudo().write({
                    'attachment_path_complete': dir_name,
                })
            return fname
        return super(IrAttachment, self)._file_write(value, checksum)

    @api.model
    def _file_read(self, fname, bin_size=False):
        r = ''
        if self._context.get('attachment_path_complete') and self._storage() == 'file':
            full_path = self._context['attachment_path_complete']
            try:
                r = base64.b64encode(open(full_path, 'rb').read())
            except (IOError, OSError):
                _logger.info("_read_file reading %s", full_path, exc_info=True)
            return r
        return super(IrAttachment, self)._file_read(fname, bin_size=bin_size)

    @api.model
    def _file_delete(self, fname):
        if self._context.get('attachment_path_complete') and self._storage() == 'file':
            try:
                os.unlink(self._context['attachment_path_complete'])
            except (OSError, IOError):
                _logger.info("_file_gc could not unlink %s", self._full_path(fname), exc_info=True)
        super(IrAttachment, self)._file_delete(fname)

    @api.model
    def create(self, vals):
        if 'name' in vals and 'ref' not in vals:
            vals['ref'] = vals['name']
        return super(IrAttachment, self).create(vals)

    def _index_pdf(self, bin_data):
        buf = u''
        _logger.info("PDF INDEX %s" % bin_data.startswith(b'%PDF-'))
        if bin_data.startswith(b'%PDF-'):
            f = io.BytesIO(bin_data)
            output_string = io.StringIO()
            try:
                parser = PDFParser(f)
                doc = PDFDocument(parser)
                rsrcmgr = PDFResourceManager()
                device = TextConverter(rsrcmgr, buf, laparams=LAParams())
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                for page in PDFPage.create_pages(doc):
                    interpreter.process_page(page)
                buf = output_string.getvalue()
            except Exception:
                pass
        return buf


irattachment._index_pdf = IrAttachment._index_pdf
