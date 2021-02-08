# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CoAbstractCodes(models.AbstractModel):
    _name = "co.abstract.codes"
    _description = "Contains the logic shared between model which allows to register codes DIAN"

    name = fields.Char("Name", required = True)
    code = fields.Char("Code", required = True)
    active= fields.Boolean("Active", default=True)
    description = fields.Char("Description")
    
    @api.constrains('code')
    def check_catalog(self):
        for catalog_id in self:
            if self.search_count([('code','=', catalog_id.code)]) > 1:
                raise ValidationError(_('Code already exists and violates unique field constrain'))
        
    @api.model
    def get_selection(self):
        res=[]
        datas=self.search([('active', '=', True)])
        if datas:
            res = [(data.code,data.name) for data in datas]
        return res
    
    @api.model
    def get_by_code(self, code):
        data=self.search([('active', '=', True),('code','=',code)], limit=1)
        return data

    