# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class IrAttachmentJournalCategory(models.Model):
    _name = "ir.attachment.journal.category"
    _description = "Attachment Category"
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _rec_name = 'complete_name'
    _order = 'parent_left'

    name = fields.Char('Name', index=True, required=True, translate=True)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name',
        store=True, translate=True)
    parent_id = fields.Many2one('ir.attachment.journal.category', 'Parent Category', index=True, ondelete='cascade')
    child_id = fields.One2many('ir.attachment.journal.category', 'parent_id', 'Child Categories')
    parent_left = fields.Integer('Left Parent', index=1)
    parent_right = fields.Integer('Right Parent', index=1)
    attachment_count = fields.Integer(
        '# Attachment files', compute='_compute_attachment_count',
        help="The number of attachment under this category (Does not consider the children categories)")
    display_name = fields.Char('Name', compute='_compute_dispay_name')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    def _compute_dispay_name(self):
        for category in self:
            category.display_name = category.name

    def _compute_attachment_count(self):
        read_group_res = self.env['ir.attachment'].read_group([('categ_id', 'child_of', self.ids)], ['categ_id'], ['categ_id'])
        group_data = dict((data['categ_id'][0], data['categ_id_count']) for data in read_group_res)
        for categ in self:
            attachment_count = 0
            for sub_categ_id in categ.search([('id', 'child_of', categ.id)]).ids:
                attachment_count += group_data.get(sub_categ_id, 0)
            categ.product_count = attachment_count

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You cannot create recursive categories.'))
        return True

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]


class IrAttachmentJournalTemplate(models.Model):
    _name = "ir.attachment.journal.template"
    _description = "Attachment Journal template"

    name = fields.Char(string='Attachment Journal Name', required=True)
    code = fields.Char(string='Short Code', size=5, required=True,
                       help="The journal entries of this Attachment journal will be named using this prefix.")
    journal_type = fields.Selection([('standard', 'Standard Attachment Journal')], string="Attachment Journal name",
                                    default="standard")
    res_model = fields.Char('Resource model')
    # res_module = fields.Char('Resource module')
    # res_name = fields.Char('Resource id')

    @api.multi
    def try_attach_companies(self):
        model = 'ir.attachment.journal'
        ir_model_data = self.env['ir.model.data']
        company_obj = self.env['res.company']
        company_ids = company_obj.search([])
        _logger.info("TEMPLATES %s(%s)" % (company_ids, self))
        for template in self:
            xml_id = template.get_external_id()
            _logger.info("GET TEMPLATE %s" % xml_id)
            if xml_id:
                res_module, res_id = tuple(xml_id[template.id].split('.'))
            else:
                continue
            _logger.info("TEMPLATE %s:%s:%s" % (company_ids, res_module, res_id))
            for company in company_ids:
                try:
                    ref = self.env.ref('%s.%s_%s' % (res_module, company.id, res_id))
                    template_xmlid = ir_model_data.search([('model', '=', model), ('res_id', '=', ref.id)])
                except ValueError:
                    ref = False
                    template_xmlid = False
                if not ref or not template_xmlid:
                    seq_name = "%s sequence" % template.name
                    seq_prefix = "%s/%%(range_year)s" % template.code
                    sequence_id = self.env['ir.sequence'].create({
                        'name': seq_name,
                        'code': template.res_model,
                        'prefix': seq_prefix,
                        'number_next': 1,
                        'number_increment': 1,
                        'use_date_range': True,
                        'company_id': company.id,
                        'padding': 6,
                    })
                    vals = {
                        'name': template.name,
                        'code': template.code,
                        'journal_type': template.journal_type,
                        'sequence_id': sequence_id.id,
                        'company_id': company.id,
                        'res_model': template.res_model,
                    }
                    new_xml_id = str(company.id) + '_' + res_id
                    ir_model_data._update(model, res_module, vals, xml_id=new_xml_id, store=True,
                                                 noupdate=True, mode='init', res_id=False)


class IrAttachmentJournal(models.Model):
    _name = "ir.attachment.journal"
    _description = "Attachment Journal"

    @api.one
    def _kanban_dashboard(self):
        self.kanban_dashboard = json.dumps(self.get_journal_dashboard_datas())

    name = fields.Char(string='Attachment Journal Name', required=True)
    code = fields.Char(string='Short Code', size=5, required=True,
                       help="The journal entries of this Attachment journal will be named using this prefix.")
    active = fields.Boolean(default=True,
                            help="Set active to false to hide the Attachment Journal without removing it.")
    journal_type = fields.Selection([('standard', 'Standard Attachment Journal')], string="Attachment Journal name",
                                    default="standard")
    res_model = fields.Char(index=True)
    sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence',
                                  help="This field contains the information related to the numbering of the "
                                       "Attachment journal entries of this journal.",
                                  required=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this journal")
    show_on_dashboard = fields.Boolean(string='Show Attachment Journal on dashboard',
                                       help="Whether this journal should be displayed on the dashboard or not",
                                       default=True)
    color = fields.Integer("Color Index", default=0)
    sequence = fields.Integer(help='Used to order Attachment Journals in the dashboard view', default=10)
    kanban_dashboard = fields.Text(compute='_kanban_dashboard')
    belongs_to_company = fields.Boolean('Belong to the user\'s current company', compute="_belong_to_company",
                                        search="_search_company_journals", )
    attachment_name = fields.Text(string='Template Name', required=False,
                                  help="For attachment store, name of the template used in the naming.")
    attachment_file = fields.Text(string='Attachment File Name', required=False, readonly=False, store=True,
                                  help="The path to the main attachment file (depending on attachment Type) or empty if "
                                       "the content is in another field")
    attachment_path = fields.Text(string='Attachment Path Name', required=False, readonly=False, store=True,
                                  help="The path to the main attachment file (depending on attachment Type) or empty if "
                                       "the content is in another field")
    attachment_root_path = fields.Text(string='Attachment Root Path Name', required=False, readonly=False, store=True,
                                  help="The path to the main attachment file (depending on attachment Type) or empty if "
                                       "the content is in another field")
    @api.multi
    @api.depends('company_id')
    def _belong_to_company(self):
        for journal in self:
            journal.belongs_to_company = (journal.company_id.id == self.env.user.company_id.id)

    @api.multi
    def _search_company_journals(self, operator, value):
        if value:
            recs = self.search([('company_id', operator, self.env.user.company_id.id)])
        elif operator == '=':
            recs = self.search([('company_id', '!=', self.env.user.company_id.id)])
        else:
            recs = self.search([('company_id', operator, self.env.user.company_id.id)])
        return [('id', 'in', [x.id for x in recs])]

    def _open_action(self):
        action_name = self._context.get('action_name', False)
        if not action_name:
            return "knowledge_action_documents"
        return action_name

    def _open_action_context(self, action):
        ctx = self._context.copy()
        action['context'] = ctx
        return action

    @api.multi
    def open_action(self):
        action_name = self._open_action()
        if action_name.find('.') != -1:
            [action] = self.env.ref(action_name).read()
        else:
            [action] = self.env.ref('knowledge.%s' % action_name).read()
        # _logger.info("ACTIONS %s" % action)
        return action

    @api.multi
    def get_journal_dashboard_datas(self):
        title = ''
        if self.res_model == 'ir.attachment':
            title = "Attachment documents"
        return {'title': title}
