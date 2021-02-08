# -*- coding: utf-8 -*-

from odoo import api, models, fields


class SaphetySerie(models.Model):
    _name = 'co.saphety.series'
    _description = "Saphety Series"

    serial_id = fields.Char("Serial ID" )
    serial_company_id = fields.Char("Company ID")
    name = fields.Char("Name")
    auth_number = fields.Char("Authorization Number")
    prefix = fields.Char("Prefix")
    valid_from = fields.Char("Valid From")
    valid_to = fields.Char("Valid To")
    start_value = fields.Char("Start Value")
    end_value = fields.Char("End Value")
    efective_value = fields.Char("Efective Value")
    document_type = fields.Char("Document Type")
    serie_type = fields.Char("Serie Type")
    technical_key = fields.Char("Technical Key")
    external_key = fields.Char("External Key")
    test_set_id = fields.Char("Test Set Id")
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('send', 'Send')], string="State", default='draft')
    
    sequence_id = fields.Many2one('ir.sequence', string="Sequence")

    _sql_constraints = [
        ('serial_id', 'unique(serial_id)', "Another serie already exists with this code!"),
    ]

    # -----------------------------------------------------
    # Crons
    # -----------------------------------------------------
    @api.model
    def _cron_update_series(self):
        SaphetyProviderEnv = self.env['co.saphety'].sudo()

        saphety_series = SaphetyProviderEnv.get_all_series()
        odoo_series = self.search([]).mapped('serial_id')

        for serie in saphety_series:
            vals = dict(
                    serial_id=serie['Id'],
                    serial_company_id=serie['CompanyId'],
                    name=serie['Name'],
                    auth_number=serie['AuthorizationNumber'],
                    prefix=serie['Prefix'],
                    valid_from=serie['ValidFrom'],
                    valid_to=serie['ValidTo'],
                    start_value=serie['StartValue'],
                    end_value=serie['EndValue'],
                    efective_value=serie['EfectiveValue'],
                    document_type=serie['DocumentType'],
                    serie_type=serie['SerieType'],
                    technical_key=serie['TechnicalKey'],
                    external_key=serie['ExternalKey'],
                    sequence_id = self._sequence_by_code(serie['Id'], serie['Name'], serie['Prefix'])
                )
            if serie['Id'] not in odoo_series:
                self.create(vals)
            else:
                serie_id = self.search([('serial_id','=',serie['Id'])])
                serie_id.write(vals)
    
    
    def _sequence_by_code(self, id, name, prefix):
        serie_id = self.search([('serial_id','=',id)])
        #sequence_id = self.env['ir.sequence'].search([('code','=','saphety.%s' % prefix)])
        
        vals = {}
        #vals['code'] = 'saphety.%s' % prefix
        vals['name'] = name
        vals['implementation'] = 'no_gap'
        vals['prefix'] = "%s-" % prefix
        vals['suffix'] = False
        vals['padding'] = 4
        vals['use_date_range'] = False
        
        if serie_id:
            serie_id.sequence_id.write(vals)
            sequence_id = serie_id.sequence_id.id
        else:
            seq = self.env['ir.sequence'].create(vals)
            sequence_id = seq.id
        return sequence_id
            
        
    
    
