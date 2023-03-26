# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import os
import shutil
import nextcloud_client

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.multi
    @job
    def _file_copy_write_nextcloud(self, fname, full_file_name):
        full_file_url = False
        for attachment in self:
            full_file_name = os.path.join(full_file_name, fname)
            dir_name = os.path.dirname(full_file_name)

            if attachment.company_id.use_davfs2:
                if not os.path.isdir(dir_name):
                    with tools.ignore(OSError):
                        os.makedirs(dir_name)
                try:
                    shutil.copy(fname, full_file_name)
                except IOError:
                    _logger.info("_file_copy_write writing %s", full_file_name, exc_info=True)
            else:
                try:
                    nc = nextcloud_client.Client(attachment.company_id.nextcloud_url)
                    nc.login(attachment.company_id.nextcloud_user, attachment.company_id.nextcloud_password)
                    dir_name_array = dir_name.split(os.sep)
                    part_curr = os.sep
                    for part in dir_name_array:
                        part_curr = os.path.join(part_curr, part)
                        nc.mkdir(part_curr)
                    full_path = self._full_path(fname)
                    if nc.put_file(full_path, full_file_name):
                        link = nc.share_file_with_link(full_path, public_upload=False, name=self.name)
                        full_file_url = link.get_link()
                except Exception as error:
                    _logger.error(u"Nextcloud can't be installed. Reason: {}".format(error))
        return os.path.dirname(full_file_name), os.path.basename(full_file_name), full_file_url

    @api.model
    def _file_write(self, value, checksum):
        full_file_name = self._context.get('attachment_nextcloud_path_complete', False)
        if full_file_name:
            full_file_name = os.path.join(self.env.user.company_id.nextcloud_basic_root, full_file_name)
            fname = super(IrAttachment, self)._file_write(value, checksum)
            dir_name, file_name, full_file_url = self.with_delay()._file_copy_write_nextcloud(fname, full_file_name)
            if full_file_url:
                self._file_delete(fname)
                self.sudo().write({
                    'attachment_path_complete': dir_name,
                    'url': full_file_url,
                    'type': 'url',
                    'store_fname': False,
                })
            return fname
        return super(IrAttachment, self)._file_write(value, checksum)

    @api.model
    def _file_read(self, fname, bin_size=False):
        full_file_name = self._context.get('attachment_nextcloud_path_complete', False)
        if full_file_name:
            full_file_name = os.path.join(full_file_name, fname)
            if self.company_id.use_davfs2:
                return super(IrAttachment, self). \
                    with_context(dict(self._context, attachment_path_complete=full_file_name)). \
                    _file_read(fname, bin_size=bin_size)
            else:
                r = ''
                try:
                    nc = nextcloud_client.Client(self.env.user.company_id.nextcloud_url)
                    nc.login(self.env.user.company_id.nextcloud_user, self.env.user.company_id.nextcloud_password)
                    r = nc.get_file_contents(full_file_name)
                except Exception as error:
                    _logger.error(u"Nextcloud can't be download content file. Reason: {}".format(error))
            return r
        return super(IrAttachment, self)._file_read(fname, bin_size=bin_size)

    @api.model
    def _file_delete(self, fname):
        full_file_name = self._context.get('attachment_nextcloud_path_complete', False)
        if full_file_name:
            for attachment in self:
                full_file_name = os.path.join(self.attachment_path_complete, fname)
                if attachment.company_id.nextcloud_url and attachment._storage() == 'file' and attachment.attachment_path_complete and attachment.type == 'url':
                    try:
                        nc = nextcloud_client.Client(self.env.user.company_id.nextcloud_url)
                        nc.login(self.env.user.company_id.nextcloud_user, self.env.user.company_id.nextcloud_password)
                        nc.delete_share(attachment.url)
                        nc.delete(full_file_name)
                        self.write({
                            'attachment_path_complete': False,
                        })
                    except Exception as error:
                        _logger.error(u"Nextcloud can't be delete file. Reason: {}".format(error))
                else:
                    if attachment.company_id.use_davfs2:
                        attachment.write({
                            'attachment_path_complete': False,
                        })
                        super(IrAttachment, self). \
                            with_context(dict(self._context, attachment_path_complete=full_file_name)). \
                            _file_delete(fname)
        else:
            super(IrAttachment, self)._file_delete(fname)
