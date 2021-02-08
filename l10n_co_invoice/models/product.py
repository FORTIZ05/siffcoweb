# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductCategory(models.Model):
    _inherit = "product.category"
    
    co_unspsc_code = fields.Char("UNSPSC Code")

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    co_product_type = fields.Selection([("general", "General"),("discount", "Discount"),("charge", "Charge"),
                                        ("pre_payment","Pre Payment")], "Colombian Type", default="general")