# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

import logging

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

SCOPES = ['basic', 'onedrive_all', 'sharepoint_dl']


class ExternalFolders(models.Model):
    _name = "external.folders"
    _description = "External folders"
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _rec_name = 'complete_name'
    _order = 'parent_left'

    name = fields.Char('Name', index=True, required=True, translate=True)
    object_id = fields.Char('Object ID')
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True)
    parent_id = fields.Many2one('external.folders', 'Parent Folder', index=True, ondelete='cascade')
    child_id = fields.One2many('external.folders', 'parent_id', 'Child Folders')
    parent_left = fields.Integer('Left Parent', index=1)
    parent_right = fields.Integer('Right Parent', index=1)
    folder_count = fields.Integer(
        '# Products', compute='_compute_folder_count',
        help="The number of products under this category (Does not consider the children categories)")


    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    def _compute_folder_count(self):
        read_group_res = self.env['external.documents'].read_group([('o365_folder_id', 'child_of', self.ids)], ['o365_folder_id'], ['o365_folder_id'])
        group_data = dict((data['o365_folder_id'][0], data['o365_folder_id_count']) for data in read_group_res)
        for folder in self:
            folder_count = 0
            for sub_folder_id in folder.search([('id', 'child_of', folder.id)]).ids:
                folder_count += group_data.get(sub_folder_id, 0)
            folder.folder_count = folder_count

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You cannot create recursive categories.'))
        return True

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]

    @api.model
    def _get_folders(self, folder_name=None, limit=1):
        res = self

        def get_child(items, list_folders, limit_total=1):
            if limit_total < 0:
                return list_folders
            limit_total -= 1
            for line in items.get_items():
                if line.is_folder:
                    parent_id = False
                    if line.parent_id:
                        parent_id = self.search([('object_id', '=', line.parent_id)])
                        if not parent_id:
                            parent_id = self.create({
                                'object_id': line.object_id,
                                'name': line.name,
                            })
                    item_id = self.search([('object_id', '=', line.object_id)])
                    if not item_id:
                        item_id = self.create({
                            'object_id': line.object_id,
                            'name': line.name,
                            'parent_id': parent_id.id,
                        })
                    list_folders |= item_id

                    # print(line.object_id, line.name)
                    list_folders = get_child(line, list_folders, limit_total=limit_total)
            return list_folders

        company_id = self.env.user.company_id
        o365_account = company_id.oauth_provider_id. \
            _get_provider(user=company_id.o365_user, password=company_id.o365_password, scopes=SCOPES)

        storage = o365_account.storage()
        drive = storage.get_drive(company_id.o365_drive_id)
        if folder_name is None:
            folders = drive.get_root_folder()
        else:
            folders = drive.get_special_folder(folder_name)
        res = get_child(folders, res, limit)
        return res

    @api.model
    def update_folders(self, folder_name=None, limit=1):
        return self._get_folders(folder_name=folder_name, limit=limit)
