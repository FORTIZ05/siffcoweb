# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    saphety_username = fields.Char("Username", config_parameter='l10n_co_saphety.saphety_username')
    saphety_password = fields.Char("Password", config_parameter='l10n_co_saphety.saphety_password')
    saphety_virtual_operator = fields.Char("Virtual Operator",
                                           config_parameter='l10n_co_saphety.saphety_virtual_operator')
    saphety_mode = fields.Selection(selection=[('https://api-factura-electronica-co-qa.saphety.com', 'Development'),
                                               ('https://api-factura-electronica-co.saphety.com', 'Production')], string='Mode',
                                               default = 'https://api-factura-electronica-co-qa.saphety.com', 
                                               config_parameter='l10n_co_saphety.saphety_mode')

    
    def action_saphety_config_wizard(self):
        context = dict(self.env.context)
        return {
            'name': _('Saphety Wizard'),
            'res_model': 'co.saphety.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('l10n_co_saphety.view_form_saphety_wizard').id,
            'context': context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }