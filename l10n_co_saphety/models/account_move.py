# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from base64 import decodestring 
from datetime import datetime, timedelta

class AccountMove(models.Model):
    _inherit = "account.move"

    co_saphety_id = fields.Char("Saphety Id", copy=False)
    co_saphety_correlation = fields.Char("Saphety Correlation", readonly=True, copy=False)
    co_saphety_invoice_date = fields.Datetime("Saphety Invoice Date", readonly=True, copy=False)
    co_saphety_cufe = fields.Char("CUFE", readonly=True, copy=False)
    co_saphety_mandate_id = fields.Many2one("res.partner", "Mandate Name")
    co_saphety_pdf = fields.Boolean("Saphety PDF", copy=False)
    
    @api.onchange('co_invoice_code')
    def onchange_co_invoice_code(self):
        if self.co_invoice_code == '91':
            if self.reversed_entry_id:
                self.co_operation_type = '20'
            else:
                self.co_operation_type = '22'
        elif self.co_invoice_code == '92':
            if self.reversed_entry_id:
                self.co_operation_type = '30'
            else:
                self.co_operation_type = '32'
        elif self.co_invoice_code == '01':
            self.co_operation_type = '10'
    
    @api.onchange('co_operation_type')
    def onchange_co_operation_type(self):
        if self.co_operation_type in ['09','10','11']:
            self.co_invoice_code = '01'
        elif self.co_operation_type in ['20','22','23']:
            self.co_invoice_code = '91'
        elif self.co_operation_type in ['30','32','33']:
            self.co_invoice_code = '92'
            
    def validate_saphety_invoice(self):
        self.ensure_one()
        errors = []
        if not self.partner_id.email:
            errors.append(_("The email is required for %s") % self.partner_id.name)
        for line_id in self.invoice_line_ids:
            if not line_id.product_id:
                errors.append(_("The product is required for %s") % line_id.name)
            if line_id.product_id.co_product_type not in ['general'] and line_id.tax_ids:
                errors.append(_("The product should not have tax for %s") % line_id.name)
            if line_id.product_id.co_product_type in ['discount'] and line_id.quantity>=0:
                errors.append(_("The quantity must be less than 0 for %s") % line_id.name)
            if line_id.product_id.co_product_type in ['charge', 'pre_payment'] and line_id.quantity<=0:
                errors.append(_("The quantity must be greater than 0 for %s") % line_id.name)
        return errors
    
    def check_saphety_document_status(self):
        for move in self:
            if not move.journal_id.co_electronic_invoice:
                continue
            if not move.co_saphety_id:
                move._validate_saphety_invoice_all()
                errors = move.validate_saphety_invoice()
                if errors:
                    raise ValidationError("\n".join(errors))
                move.saphety_send_documents()
            self.env['co.saphety'].check_document_status(move)
            if not move.co_saphety_pdf:
                self.env['co.saphety'].get_document_pdf(move)

    @api.model
    def check_saphety_pdf_invoices(self):
        days_before = fields.Date.context_today(self)
        invoice_ids = self.search([('co_saphety_pdf','=',False),('journal_id.co_electronic_invoice','=',True),('type','in',['out_invoice', 'out_refund']),
                                   ('invoice_date','=',days_before),('co_events','in',['02','030'])])
        if invoice_ids:
            invoice_ids.check_saphety_document_status()
    
    @api.model
    def check_saphety_status_invoices(self):
        days_before = fields.Date.context_today(self) - timedelta(days=7)
        invoice_ids = self.search([('co_events','in',['02','030']),('journal_id.co_electronic_invoice','=',True),('type','in',['out_invoice', 'out_refund']),
                                   ('invoice_date','>=',days_before)])
        if invoice_ids:
            invoice_ids.check_saphety_document_status()
    
    def get_saphety_datetime(self):
        self.ensure_one()
        if self.invoice_date:
            today = fields.Datetime.now()
            if not self.co_saphety_invoice_date:
                if today.date() > self.invoice_date:
                    self.co_saphety_invoice_date = "%s 23:55:59" % fields.Date.to_string(self.invoice_date) 
                else:
                    self.co_saphety_invoice_date = fields.Datetime.to_string(fields.Datetime.context_timestamp(self.with_context(tz='America/Bogota'), datetime.now()))
            else:
                if self.co_saphety_invoice_date.date() != self.invoice_date:
                    self.co_saphety_invoice_date = "%s 23:55:59" % fields.Date.to_string(self.invoice_date)

    def saphety_send_documents(self):
        for move in self:
            if move.is_invoice(include_receipts=True) and move.type in ['out_invoice', 'out_refund']:
                self.get_saphety_datetime()
                if move.journal_id.co_electronic_invoice:
                    if not move.co_saphety_id:
                        res = self.env['co.saphety'].send_documents(move)
                    self.with_context(co_no_validate=True).env['co.saphety'].check_document_status(move)
                
    
    def _validate_saphety_invoice_all(self):
        for move in self:
            if move.is_invoice(include_receipts=True) and move.type in ['out_invoice', 'out_refund'] and move.journal_id.co_electronic_invoice:
                if not move.invoice_line_ids:
                    raise ValidationError(_("It is necessary to have at least one line"))
                if move.type == 'out_invoice' and move.co_operation_type in ['20','22','23']:
                    raise ValidationError(_("You cannot create a credit note"))
                elif move.type == 'out_refund' and move.co_operation_type in ['09','10','11', '30','32','33']:
                    raise ValidationError(_("Cannot create invoice or debit note"))
                if move.co_operation_type in ['09','10','11'] and move.co_invoice_code not in ['01','02','03','04']:
                    raise ValidationError(_("Cannot create Invoice 'Invoice Type Code' is bad"))
                if move.co_operation_type in ['20','22','23'] and move.co_invoice_code != '91':
                    raise ValidationError(_("Cannot create Credit Note 'Invoice Type Code' is bad"))
                if move.co_operation_type in ['30','32','33'] and move.co_invoice_code != '92':
                    raise ValidationError(_("Cannot create Debit Note 'Invoice Type Code' is bad"))
    
    def post(self):
        super(AccountMove, self).post()
        self._validate_saphety_invoice_all()
        try:
            self.saphety_send_documents()
        except Exception:
            pass
    
    def button_draft(self):
        move_ids = self.filtered(lambda move: move.journal_id.co_electronic_invoice==True and move.state in ['posted'] and move.co_saphety_id!=False)
        if move_ids and not self.env.context.get('co_saphety_refund'):
            raise ValidationError(_("You cannot draft a document sent to Saphety"))
        return super(AccountMove, self).button_draft()
    
    def _reverse_move_vals(self, default_values, cancel=True):
        if self.env.context.get("is_co_debit_note"):
            default_values['co_operation_type'] = '30'
        else:
            default_values['co_operation_type'] = '20'
        return super(AccountMove, self)._reverse_move_vals(default_values, cancel=cancel)
    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_co_all_taxes(self, price_unit=None, quantity=None, discount=None, move_type=None, currency=None, 
                          product=None, partner=None, taxes=None, company=None, date=None):
        self.ensure_one()
        price_unit=price_unit or self.price_unit
        quantity=quantity or self.quantity
        if discount == None:
            discount=self.discount    
        currency=currency or self.currency_id
        product=product or self.product_id
        partner=partner or self.partner_id
        taxes=taxes or self.tax_ids
        move_type=move_type or self.move_id.type
        
        price_unit_wo_discount = price_unit * (1 - (discount / 100.0))
        subtotal = quantity * price_unit_wo_discount

        res = {}
        if taxes:
            res = taxes._origin.compute_all(price_unit_wo_discount, quantity=quantity, currency=currency, product=product, 
                                                  partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
        return res