# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _

class UoM(models.Model):
    _inherit = 'uom.uom'
    
    co_unit_code_id = fields.Many2one("co.code.product", string="Unit Code") 
    co_unit_code = fields.Selection(selection="_get_co_unit_code", string="Code")
    
    @api.onchange('co_unit_code_id')
    def _onchange_co_unit_code_id(self):
        if self.co_unit_code_id:
            self.co_unit_code = self.co_unit_code_id.code
        return {}
    
    @api.model
    def _get_co_unit_code(self):
        return self.env['co.code.product'].get_selection()