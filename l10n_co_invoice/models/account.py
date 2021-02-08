# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    co_credit_note_id = fields.Many2one(comodel_name="account.journal", string="Credit Note", domain="[('type','in', ['sale', 'purchase'])]")
    co_debit_note_id = fields.Many2one(comodel_name="account.journal", string="Debit Note", domain="[('type','in', ['sale', 'purchase'])]")
    co_invoice_code = fields.Selection(selection="_get_co_invoice_code", string="Invoice Type Code")
    co_credit_invoice_code = fields.Selection(selection="_get_co_invoice_code", string="Credit Invoice Type Code")
    co_debit_invoice_code = fields.Selection(selection="_get_co_invoice_code", string="Debit Invoice Type Code")
    
    co_debit_sequence = fields.Boolean(string='Dedicated Debit Note Sequence', help="Check this box if you don't want to share the same sequence for invoices and debit notes made from this journal", default=False)
    co_debit_sequence_id = fields.Many2one('ir.sequence', string='Debit Note Entry Sequence',
        help="This field contains the information related to the numbering of the debit note entries of this journal.", copy=False)
    
    co_debit_sequence_number_next = fields.Integer(string='Debit Notes Next Number',
        help='The next sequence number will be used for the next debit note.', 
        compute='_compute_co_debit_sequence_number_next',
        inverse='_inverse_co_debit_sequence_number_next')
    
    co_electronic_invoice = fields.Boolean("Electronic Invoice?")
    
    @api.model
    def _get_co_invoice_code(self):
        return self.env['co.code.document'].get_selection()
    
    @api.onchange('co_invoice_code')
    def _onchange_co_invoice_code(self):
        if self.co_invoice_code:
            if self.co_invoice_code in ['01','02', '03', '04']:
                self.co_credit_invoice_code = '91'
                self.co_debit_invoice_code = '92'
        return {}
    
    @api.depends('co_debit_sequence_id.use_date_range', 'co_debit_sequence_id.number_next_actual')
    def _compute_co_debit_sequence_number_next(self):
        for journal in self:
            if journal.co_debit_sequence_id and journal.co_debit_sequence:
                sequence = journal.co_debit_sequence_id._get_current_sequence()
                journal.co_debit_sequence_number_next = sequence.number_next_actual
            else:
                journal.co_debit_sequence_number_next = 1

    def _inverse_co_debit_sequence_number_next(self):
        for journal in self:
            if journal.co_debit_sequence_id and journal.co_debit_sequence and journal.co_debit_sequence_number_next:
                sequence = journal.co_debit_sequence_id._get_current_sequence()
                sequence.sudo().number_next = journal.co_debit_sequence_number_next
    
    
    def write(self, vals):
        # create the relevant refund sequence
        if vals.get('co_debit_sequence'):
            for journal in self.filtered(lambda j: j.type in ('sale', 'purchase') and not j.co_debit_sequence_id):
                journal_vals = {
                    'name': journal.name,
                    'company_id': journal.company_id.id,
                    'code': journal.code,
                    'refund_sequence_number_next': vals.get('co_debit_sequence_number_next', journal.co_debit_sequence_number_next),
                }
                journal.co_debit_sequence_id = self.sudo()._create_sequence(journal_vals, refund=True).id
        res = super(AccountJournal, self).write(vals)
        return res
        
    @api.model
    def create(self, vals):
        if vals.get('type') in ('sale', 'purchase') and vals.get('co_debit_sequence') and not vals.get('co_debit_sequence_id'):
            vals.update({'co_debit_sequence_id': self.sudo()._create_sequence(vals, refund=True).id})
        res = super(AccountJournal, self).create(vals)
        return res

class AccountTax(models.Model):
    _inherit = 'account.tax'

    co_tax_type_id = fields.Many2one(comodel_name="co.code.tax", string="Tax Type")
    
    