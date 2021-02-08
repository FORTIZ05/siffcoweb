# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime

class PosOrder(models.Model):
    _inherit = "pos.order"
    
    def _prepare_invoice_vals(self):
        res = super(PosOrder, self)._prepare_invoice_vals()
        res['co_invoice_code'] = self.amount_total>0 and '01' or '91'
        res['co_credit_note_code'] = self.amount_total<=0 and '2' or False
        res['co_operation_type'] = self.amount_total>0 and '10' or '22'
        res['co_payment_means'] = '1'
        journal_ids = self.payment_ids.mapped('payment_method_id').mapped('cash_journal_id').filtered(lambda s: s.type == 'cash')
        res['co_payment_means_code'] =  journal_ids and  '10' or '1'
        return res