# coding: utf-8

from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    #co_tax_level_code = fields.Selection(selection="_get_co_tax_level_code", string="Tax Level Code")
    co_tax_level = fields.Selection(selection="_get_co_tax_level", string="Tax Level")
    co_legal_type = fields.Selection(selection="_get_co_legal_type", string="Legal Type")
    co_tax_level_code_ids = fields.Many2many(comodel_name="co.code.tax.level.code", string="Tax Level Code")
    
    co_first_name = fields.Char("First Name")
    co_middle_name = fields.Char("Middle Name")
    co_family_name = fields.Char("Family Name")
    
    @api.onchange('co_first_name','co_middle_name','co_family_name')
    def onchange_person_data(self):
        if self.company_type == 'person':
            name = ""
            if self.co_first_name:
                name+= self.co_first_name
            if self.co_middle_name:
                name+= " %s" % self.co_middle_name
            if self.co_family_name:
                name+= ", %s" % self.co_family_name
            self.name = name
    
    @api.model
    def _get_co_tax_level_code(self):
        return self.env['co.code.tax.level.code'].get_selection()
    
    @api.model
    def _get_co_tax_level(self):
        return self.env['co.code.tax.level'].get_selection()
    
    @api.model
    def _get_co_legal_type(self):
        return self.env['co.code.additional.account'].get_selection()