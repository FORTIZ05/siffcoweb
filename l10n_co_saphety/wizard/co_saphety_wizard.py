import logging

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

_log = logging.getLogger(__name__)


class CoSaphetyWizard(models.TransientModel):
    _name = 'co.saphety.wizard'
    _description = "Colombian Electronic Invoice using Saphety Wizard"
    
    @api.model
    def default_saphety_username(self):
        ConfigParamEnv = self.env['ir.config_parameter'].sudo()
        saphety_username = ConfigParamEnv.get_param('l10n_co_saphety.saphety_username')
        return saphety_username
    
    @api.model
    def default_saphety_password(self):
        ConfigParamEnv = self.env['ir.config_parameter'].sudo()
        saphety_password = ConfigParamEnv.get_param('l10n_co_saphety.saphety_password')
        return saphety_password
    
    @api.model
    def default_saphety_virtual_operator(self):
        ConfigParamEnv = self.env['ir.config_parameter'].sudo()
        saphety_virtual_operator = ConfigParamEnv.get_param('l10n_co_saphety.saphety_virtual_operator')
        return saphety_virtual_operator
    
    @api.model
    def default_saphety_mode(self):
        ConfigParamEnv = self.env['ir.config_parameter'].sudo()
        saphety_mode = ConfigParamEnv.get_param('l10n_co_saphety.saphety_mode')
        return saphety_mode
    
    @api.model
    def _get_default_journal(self):
        journal_id = self.env['account.journal'].search([('type','=','sale')], limit=1)
        return journal_id.id
    
    saphety_username = fields.Char("Username", default=default_saphety_username, required=True)
    saphety_password = fields.Char("Password", default=default_saphety_password, required=True)
    saphety_virtual_operator = fields.Char("Virtual Operator",
                                           default=default_saphety_virtual_operator, required=True)
    saphety_mode = fields.Selection(selection=[('https://api-factura-electronica-co-qa.saphety.com', 'Development'),
                                               ('https://api-factura-electronica-co.saphety.com', 'Production')], string='Mode',
                                               default = default_saphety_mode, required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company,
        help="Company related to this journal")
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, domain="[('company_id', '=', company_id),('type','=','sale')]", default=_get_default_journal,
                                 help="Default Journal for Electronic Invoice")
    vat = fields.Char("NIT", required=True)
    
    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.vat = self.company_id.vat
    
    def confirm_saphety_company(self):
        self.ensure_one()
        ConfigParamEnv = self.env['ir.config_parameter'].sudo()
        ConfigParamEnv.set_param('l10n_co_saphety.saphety_username', self.saphety_username)
        ConfigParamEnv.set_param('l10n_co_saphety.saphety_password', self.saphety_password)
        ConfigParamEnv.set_param('l10n_co_saphety.saphety_virtual_operator', self.saphety_virtual_operator)
        ConfigParamEnv.set_param('l10n_co_saphety.saphety_mode', self.saphety_mode)
        #self.env['res.company']._update_all_saphety_codes()
        self.company_id.vat = self.vat
        self.env['co.saphety'].get_company_information(self.company_id)
        self.env['co.saphety.series']._cron_update_series()
        vals = {}
        vals['co_electronic_invoice'] = True
        vals['co_invoice_code'] = '01'
        vals['co_credit_invoice_code'] = '91'
        vals['co_debit_invoice_code'] = '92'
        vals['co_debit_sequence'] = True
        if self.company_id.saphety_key:
            invoice_serial_id = self.env['co.saphety.series'].search([('serial_company_id','=',self.company_id.saphety_key),('document_type','=','SalesInvoice')], limit=1)
            if invoice_serial_id:
                vals['co_saphety_invoice'] = invoice_serial_id.id
                vals['sequence_id'] = invoice_serial_id.sequence_id.id
            credit_serial_id = self.env['co.saphety.series'].search([('serial_company_id','=',self.company_id.saphety_key),('document_type','=','CreditNote')], limit=1)
            if credit_serial_id:
                vals['co_saphety_credit_note'] = credit_serial_id.id
                vals['refund_sequence_id'] = credit_serial_id.sequence_id.id
            debit_serial_id = self.env['co.saphety.series'].search([('serial_company_id','=',self.company_id.saphety_key),('document_type','=','DebitNote')], limit=1)
            if debit_serial_id:
                vals['co_saphety_debit_note'] = debit_serial_id.id
                vals['co_debit_sequence_id'] = debit_serial_id.sequence_id.id
        