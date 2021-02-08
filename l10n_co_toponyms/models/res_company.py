
from odoo import models, api, fields


class ResCompany(models.Model):

    _inherit = "res.company"

    city_id = fields.Many2one('res.city', string='City of Address', compute="_compute_address")
    
    def _get_company_address_fields(self, partner):
        res = super(ResCompany, self)._get_company_address_fields(partner)
        res['city_id'] = partner.city_id.id
        return res