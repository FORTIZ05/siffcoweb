# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class Company(models.Model):
    _inherit = "res.company"

    saphety_key = fields.Char("Company Saphety Key")
    
    @api.model
    def _update_all_saphety_codes(self):
        self.env['co.code.operation.type'].update_saphety_codes()
        self.env['co.code.identifier'].update_saphety_codes()
        self.env['co.code.tax'].update_saphety_codes()
        self.env['co.code.additional.account'].update_saphety_codes()
        self.env['co.code.tax.level'].update_saphety_codes()
        self.env['co.code.tax.level.code'].update_saphety_codes()
        self.env['co.code.payment.means'].update_saphety_codes()
        self.env['co.code.payment.means.code'].update_saphety_codes()
        self.env['co.code.product'].update_saphety_codes()
        self.env['co.code.responsibility'].update_saphety_codes()
        
        
        
        