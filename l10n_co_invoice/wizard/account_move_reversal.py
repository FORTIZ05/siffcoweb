# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMoveReversal(models.TransientModel):

    _inherit = 'account.move.reversal'
    
    co_debit_note_code = fields.Selection(selection="_get_co_debit_note_type", string="Dedit Note Code")
    co_credit_note_code = fields.Selection(selection="_get_co_credit_note_type", string="Credit Note Code")
    
    @api.model
    def _get_co_debit_note_type(self):
        return self.env['co.code.debit.note.code'].get_selection()
    
    @api.model
    def _get_co_credit_note_type(self):
        return self.env['co.code.credit.note.code'].get_selection()
    