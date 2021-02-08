# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = "account.move"
    
    @api.model
    def _get_default_co_invoice_code(self):
        type = self.env.context.get('default_type')
        co_invoice_code = False
        if type in ['out_refund','in_refund']:
            co_invoice_code = '91'
        else:
            co_invoice_code = '01'
        return co_invoice_code
    
    co_invoice_code = fields.Selection(selection="_get_co_invoice_code", string="Invoice Type Code", default = _get_default_co_invoice_code,
                                       index=True, readonly=True, states={'draft': [('readonly', False)]})
    co_debit_note_code = fields.Selection(selection="_get_co_debit_note_type", string="Dedit Note Code",  
                                          readonly=True, states={'draft': [('readonly', False)]})
    co_credit_note_code = fields.Selection(selection="_get_co_credit_note_type", string="Credit Note Code", readonly=True, 
                                           states={'draft': [('readonly', False)]})
    co_payment_means = fields.Selection(selection="_get_co_payment_means", string="Payment Means", readonly=True, 
                                           states={'draft': [('readonly', False)]})
    co_payment_means_code = fields.Selection(selection="_get_co_payment_means_code", string="Payment Means Code", readonly=True, 
                                           states={'draft': [('readonly', False)]})
    co_operation_type = fields.Selection("_get_co_operation_type", string= "Type of operation", 
                                              readonly=True, states={'draft': [('readonly', False)]})
    co_events = fields.Selection("_get_co_events", string= "Type of events",
                                              readonly=True, copy=False)
    
    @api.model
    def _get_co_events(self):
        return self.env['co.code.event'].get_selection()
    
    @api.model
    def _get_co_operation_type(self):
        return self.env['co.code.operation.type'].get_selection()
    
    @api.model
    def _get_co_credit_note_type(self):
        return self.env['co.code.credit.note.code'].get_selection()
    
    @api.model
    def _get_co_invoice_code(self):
        return self.env['co.code.document'].get_selection()
    
    @api.model
    def _get_co_debit_note_type(self):
        return self.env['co.code.debit.note.code'].get_selection()
    
    @api.model
    def _get_co_payment_means(self):
        return self.env['co.code.payment.means'].get_selection()
    
    @api.model
    def _get_co_payment_means_code(self):
        return self.env['co.code.payment.means.code'].get_selection()
    
    def co_recompute_dynamic_lines(self):
        for invoice_id in self:
            invoice_id._onchange_currency()
            invoice_id._recompute_dynamic_lines(recompute_all_taxes=True)   
        return True
    
    def _recompute_tax_lines(self, recompute_tax_base_amount = False):
        context = dict(self.env.context)
        context['co_show_all_taxes'] = True
        super(AccountMove, self.with_context(**context))._recompute_tax_lines(recompute_tax_base_amount=recompute_tax_base_amount)
    
    @api.depends('line_ids.price_subtotal', 'line_ids.tax_base_amount', 'line_ids.tax_line_id', 'partner_id', 'currency_id')
    def _compute_invoice_taxes_by_co_group(self):
        self.ensure_one()
        move = self
        tax_lines = self.line_ids.filtered(lambda line: line.tax_line_id)
        res = {}
        done_taxes = set()
        for line in tax_lines:
            res.setdefault(line.tax_line_id.tax_group_id, {'base': 0.0, 'amount': 0.0})
            res[line.tax_line_id.tax_group_id]['amount'] += line.price_subtotal
            res[line.tax_line_id.tax_group_id]['tax_id'] = line.tax_line_id.id
            tax_key_add_base = tuple(self._get_tax_key_for_group_add_base(line))
            if tax_key_add_base not in done_taxes:
                if line.currency_id != self.company_id.currency_id:
                    amount = self.company_id.currency_id._convert(line.tax_base_amount, line.currency_id, self.company_id, line.date or fields.Date.today())
                else:
                    amount = line.tax_base_amount
                res[line.tax_line_id.tax_group_id]['base'] += amount
                done_taxes.add(tax_key_add_base)
        res = sorted(res.items())
        return  res
    
    @api.depends('line_ids.price_subtotal', 'line_ids.tax_base_amount', 'line_ids.tax_line_id', 'partner_id', 'currency_id')
    def _compute_invoice_taxes_by_co_code(self):
        self.ensure_one()
        move = self
        tax_lines = self.line_ids.filtered(lambda line: line.tax_line_id)
        res = {}
        done_taxes = set()
        for line in tax_lines:
            res.setdefault(line.tax_line_id.co_tax_type_id.code, {'base': 0.0, 'amount': 0.0})
            res[line.tax_line_id.co_tax_type_id.code]['amount'] += line.price_subtotal
            res[line.tax_line_id.co_tax_type_id.code]['tax_id'] = line.tax_line_id.id
            tax_key_add_base = tuple(self._get_tax_key_for_group_add_base(line))
            if tax_key_add_base not in done_taxes:
                if line.currency_id != self.company_id.currency_id:
                    amount = self.company_id.currency_id._convert(line.tax_base_amount, line.currency_id, self.company_id, line.date or fields.Date.today())
                else:
                    amount = line.tax_base_amount
                res[line.tax_line_id.co_tax_type_id.code]['base'] += amount
                done_taxes.add(tax_key_add_base)
        res = sorted(res.items())
        return  res
    
    #def _recompute_tax_lines(self, recompute_tax_base_amount = False):
    #    context = dict(self.env.context)
    #    context['co_show_all_taxes'] = True
    #    super(AccountMove, self.with_context(**context))._recompute_tax_lines(recompute_tax_base_amount=recompute_tax_base_amount)
    
    def action_reverse_co_debit(self):
        action = self.env.ref('l10n_co_invoice.action_view_account_move_debit').read()[0]
        if self.is_invoice():
            action['name'] = _('Debit Note')
        return action
    
    
    
    def _get_sequence(self):
        res = super(AccountMove, self)._get_sequence()
        journal = self.journal_id
        if journal.co_debit_sequence and self.co_invoice_code == '92':
            return journal.co_debit_sequence_id
        return res
    
    def _reverse_move_vals(self, default_values, cancel=True):
        if self.env.context.get("is_co_debit_note"):
            reverse_type_map = {
                'entry': 'entry',
                'out_invoice': 'out_invoice',
                'in_invoice': 'in_invoice',
                'in_refund': 'in_invoice',
                'out_refund': 'out_invoice',
                'out_receipt': 'out_receipt',
                'in_receipt': 'in_receipt',
            }
            type = default_values['type']
            default_values['type'] = reverse_type_map.get(self.type) or type
        res = super(AccountMove, self)._reverse_move_vals(default_values, cancel=cancel)
        return res
    
    # reversed_entry_id
    def _reverse_moves(self, default_values_list=None, cancel=False):
        for i in range(len(default_values_list)):
            vals = default_values_list[i]
            val = {}
            journal_id= default_values_list[i].get('journal_id')
            if journal_id and not self.env.context.get("is_co_debit_note"):
                journal = self.env['account.journal'].browse(journal_id)
                val['journal_id'] = journal.co_credit_note_id and journal.co_credit_note_id.id or journal.id
                val['co_invoice_code'] = journal.co_credit_note_id and journal.co_credit_note_id.co_invoice_code or journal.co_invoice_code
                if not journal.co_debit_note_id.co_invoice_code and journal.refund_sequence:
                    val['co_invoice_code'] =  journal.co_credit_invoice_code
            elif journal_id and self.env.context.get("is_co_debit_note"):
                journal = self.env['account.journal'].browse(journal_id)
                val['journal_id'] =  journal.co_debit_note_id and journal.co_debit_note_id.id or journal.id
                val['co_invoice_code'] = journal.co_debit_note_id and journal.co_debit_note_id.co_invoice_code or journal.co_invoice_code
                if not journal.co_debit_note_id.co_invoice_code and journal.co_debit_sequence:
                    val['co_invoice_code'] =  journal.co_debit_invoice_code
            if self.env.context.get('default_co_credit_note_code'):
                val['co_credit_note_code'] = self.env.context.get('default_co_credit_note_code')
            if self.env.context.get('default_co_debit_note_code'):
                val['co_debit_note_code'] = self.env.context.get('default_co_debit_note_code')
            if val:
                vals.update(val)
                default_values_list[i] = vals
        res = super(AccountMove, self)._reverse_moves(default_values_list=default_values_list, cancel=cancel)
        if self.env.context.get("is_co_debit_note"):
            for move in res.with_context(check_move_validity=False):
                for line in move.invoice_line_ids:
                    line.price_unit = abs(line.price_unit)
                    line.recompute_tax_line = True
                #    if line.currency_id:
                #        line._onchange_currency()
                #move._onchange_invoice_line_ids()
                move._onchange_currency()   
                move._check_balanced()
        return res
    
    def post(self):
        super(AccountMove, self).post()
    
    def _get_co_default_journal(self):
        self.ensure_one()
        
        if self.co_invoice_code:
            journal = self.journal_id
            type = journal.type
            journal_id = self.env['account.journal'].search([('co_invoice_code','=',self.co_invoice_code),
                                                             ('type','=',type),
                                                             ('company_id','=',self.company_id.id)], limit = 1)
            if not journal_id and self.co_invoice_code == '91':
                journal_id = self.env['account.journal'].search([('co_credit_invoice_code','=',self.co_invoice_code),
                                                                 ('type','=',type), 
                                                                 ('company_id','=',self.company_id.id),
                                                                 ('refund_sequence','=',True)], limit = 1)
            elif not journal_id and self.co_invoice_code == '92':
                journal_id = self.env['account.journal'].search([('co_debit_invoice_code','=',self.co_invoice_code),
                                                                 ('type','=',type), 
                                                                 ('company_id','=',self.company_id.id),
                                                                 ('co_debit_sequence','=',True)], limit = 1)
            self.journal_id = journal_id.id or journal.id
            
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        if self.type in ['out_invoice', 'in_invoice', 'in_refund', 'out_refund']:
            if not self.co_invoice_code and self.partner_id:
                if self.type in ['in_refund', 'out_refund']:
                    self.co_invoice_code = '91'
                else:
                    self.co_invoice_code = '01'
            self._get_co_default_journal()
        return res
    
    @api.onchange('co_invoice_code')
    def _onchange_co_invoice_code(self):
        self._get_co_default_journal()
        return {}
            
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    

