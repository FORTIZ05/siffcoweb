
from odoo import fields, models


class City(models.Model):
    _inherit = "res.city"

    co_code = fields.Char('Code')
