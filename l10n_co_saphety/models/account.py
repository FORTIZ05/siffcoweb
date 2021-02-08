# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    
    co_saphety_invoice = fields.Many2one(comodel_name="co.saphety.series", string="Invoice Series")
    co_saphety_credit_note = fields.Many2one(comodel_name="co.saphety.series", string="Credit Note Series")
    co_saphety_debit_note = fields.Many2one(comodel_name="co.saphety.series", string="Debit Note Series")
    
    #@api.onchange('co_saphety_invoice', 'co_saphety_credit_note', 'co_saphety_debit_note')
    #def _onchange_saphety_series(self):
    #    if self.co_saphety_invoice:
    #        self.write({'sequence_id':self.co_saphety_invoice.sequence_id})
            #self.sequence_id = self.co_saphety_invoice.sequence_id
    #    if self.co_saphety_credit_note:
    #        self.write({'refund_sequence_id':self.co_saphety_credit_note.sequence_id})
            #self.refund_sequence_id = self.co_saphety_credit_note.sequence_id
    #    if self.co_saphety_debit_note:
    #        self.write({'co_debit_sequence_id':self.co_saphety_debit_note.sequence_id})
            #self.co_debit_sequence_id = self.co_saphety_debit_note.sequence_id
    
    def write(self, vals):
        if vals.get('co_saphety_invoice'):
            co_saphety_invoice = self.env['co.saphety.series'].browse(vals.get('co_saphety_invoice'))
            vals['sequence_id'] = co_saphety_invoice.sequence_id.id
        if vals.get('co_saphety_credit_note'):
            co_saphety_credit_note = self.env['co.saphety.series'].browse(vals.get('co_saphety_credit_note'))
            vals['refund_sequence_id'] = co_saphety_credit_note.sequence_id.id
        if vals.get('co_saphety_debit_note'):
            co_saphety_debit_note = self.env['co.saphety.series'].browse(vals.get('co_saphety_debit_note'))
            vals['co_debit_sequence_id'] = co_saphety_debit_note.sequence_id.id
        res = super(AccountJournal, self).write(vals)
        return res
        
    @api.model
    def create(self, vals):
        if vals.get('co_saphety_invoice'):
            co_saphety_invoice = self.env['co.saphety.series'].browse(vals.get('co_saphety_invoice'))
            vals['sequence_id'] = co_saphety_invoice.sequence_id.id
        if vals.get('co_saphety_credit_note'):
            co_saphety_credit_note = self.env['co.saphety.series'].browse(vals.get('co_saphety_credit_note'))
            vals['refund_sequence_id'] = co_saphety_credit_note.sequence_id.id
        if vals.get('co_saphety_debit_note'):
            co_saphety_debit_note = self.env['co.saphety.series'].browse(vals.get('co_saphety_debit_note'))
            vals['co_debit_sequence_id'] = co_saphety_debit_note.sequence_id.id
        res = super(AccountJournal, self).create(vals)
        return res