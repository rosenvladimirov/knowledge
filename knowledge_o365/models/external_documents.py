# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging
import os
import shutil
import tempfile

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)

SCOPES = ['basic', 'onedrive_all', 'sharepoint_dl']


class ExternalDocuments(models.Model):
    _inherit = 'external.documents'

    o365_folder = fields.Selection(string='O365 Folder',
                                   selection=lambda self: self._selection_type_assets())
    o365_item_id = fields.Char('o365 Item ID')
    o365_checklist_item_id = fields.Char('o365 Checklist Item ID')

    @api.multi
    @job
    def _file_copy_write_o365(self, fname, dir_name):
        for attachment in self:
            try:
                o365_account = attachment.company_id.oauth_provider_id. \
                    _get_provider(user=attachment.company_id.o365_user, password=attachment.company_id.o365_password,
                                  scopes=SCOPES)
                storage = o365_account.storage()
                drive = storage.get_default_drive(attachment.company_id.drive_id)
                if attachment.o365_folder:
                    folder = drive.get_item(attachment.o365_folder)
                else:
                    folder = drive.get_special_folder(dir_name)
                file = folder.upload(item=fname)
                if file:
                    self.sudo().write({
                        'o365_item_id': file.object_id,
                        'o365_folder': folder and folder.object_id or False,
                        'o365_checklist_item_id': False,
                    })
                permission = file.share_with_link(share_type='edit')
                if permission:
                    self.sudo().write({
                        'url': permission.share_link,
                        'type': 'url',
                        'store_fname': False,
                        'o365_item_id': False,
                        'o365_checklist_item_id': file.object_id,
                    })
                    self._file_delete(fname)
            except Exception as error:
                _logger.error(u"Office 365 can't be upload content file. Reason: {}".format(error))

    @api.model
    def _file_write(self, value, checksum):
        dir_name = self._context.get('attachment_o365_path_complete', False)
        if self.company_id.oauth_provider_id:
            fname = super(IrAttachment, self)._file_write(value, checksum)
            self.with_delay()._file_copy_write_o365(fname, dir_name)
            return fname
        return super(IrAttachment, self)._file_write(value, checksum)

    @api.model
    def _file_read(self, fname, bin_size=False):
        if self.o365_item_id and not self.full_file_url:
            r = ''
            try:
                o365_account = self.company_id.oauth_provider_id. \
                    _get_provider(user=self.company_id.o365_user, password=self.company_id.o365_password,
                                  scopes=SCOPES)
                storage = o365_account.storage()
                drive = storage.get_default_drive(self.company_id.drive_id)
                item = drive.get_item(self.o365_item_id)
                with tempfile.TemporaryDirectory() as to_folder:
                    r = item.download(to_path=to_folder)
                    full_path = os.path.join(to_folder, item.name)
                    r = base64.b64encode(open(full_path, 'rb').read())
            except Exception as error:
                _logger.error(u"Office 365 can't be download content file. Reason: {}".format(error))
            return r
        return super(IrAttachment, self)._file_read(fname, bin_size=bin_size)

    @api.model
    def _file_delete(self, fname):
        if self.o365_item_id:
            try:
                o365_account = self.company_id.oauth_provider_id. \
                    _get_provider(user=self.company_id.o365_user, password=self.company_id.o365_password,
                                  scopes=SCOPES)
                storage = o365_account.storage()
                drive = storage.get_default_drive(self.company_id.drive_id)
                item = drive.get_item(self.o365_item_id)
                if not item.delete():
                    _logger.error(u"Office 365 can't be delete content file: {}".format(item.name))
            except Exception as error:
                _logger.error(u"Office 365 can't be delete content file. Reason: {}".format(error))
        super(IrAttachment, self)._file_delete(fname)

    @api.model
    def _get_folders(self):
        o365_account = self.company_id.oauth_provider_id. \
            _get_provider(user=self.company_id.o365_user, password=self.company_id.o365_password, scopes=SCOPES)
        res = []
        storage = o365_account.storage()
        drive = storage.get_default_drive(self.company_id.drive_id)
        root_folder = drive.get_root_folder()
        for item in root_folder.get_items():
            if item.is_folder():
                res.append((item.object_id, item.name))
        return res
