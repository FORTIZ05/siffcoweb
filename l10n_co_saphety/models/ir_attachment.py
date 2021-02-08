from odoo import models, api, fields, _

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    
    co_saphety_send = fields.Boolean("Is send")