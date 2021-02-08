# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CoAbstractCodes(models.AbstractModel):
    _inherit = "co.abstract.codes"
    
    saphety = fields.Boolean("Is Saphety Code")
    
    @api.model
    def update_saphety_codes(self):
        return False
    
    def check_saphety_code(self, codes):
        self.search(["|",('active','=',False),('active','=',True)]).write({'active':False, 'saphety':False})
        for code in codes:
            code_id = self.search([('code','=',code.get('Code',False)),"|",('active','=',False),('active','=',True)], limit=1)
            if code_id:
                code_id.saphety = True
                code_id.active = True
            else:
                self.create({'code':code.get('Code',False), 'name':code.get('Name',False), 'saphety':True})
        self.search([('saphety','=',False)]).write({'active':False})

# class CoCodeDocument(models.Model):
#     _name = "co.code.document"
#     _inherit = 'co.abstract.codes'
#     _description = "Tipo de Documento"
# 
#     _order = "code ASC, id ASC"
# 
# class CoCodeDocumentReference(models.Model):
#     _name = "co.code.document.reference"
#     _inherit = 'co.abstract.codes'
#     _description = "Referencia a documentos no trib"
# 
#     _order = "code ASC, id ASC"
# 
# # Falta Referencia a documentos no trib
# 
class CoCodeOperationType(models.Model):
    _inherit = 'co.code.operation.type'
    
    @api.model
    def update_saphety_codes(self):
        codes = self.env['co.saphety'].get_co_codes('v2/dataelements/docoperationtypes')
        self.check_saphety_code(codes)
    
    @api.model
    def get_selection(self):
        res=[]
        datas=self.search([('active', '=', True),('saphety','=',True)])
        if datas:
            res = [(data.code,data.name) for data in datas]
        return res
# 
# class CoCodeOperationTypeHealth(models.Model):
#     _name = "co.code.operation.type.health"
#     _inherit = 'co.abstract.codes'
#     _description = "Tipos de operación Salud"
# 
#     _order = "code ASC, id ASC"
# 
# class CoCodeCreditNote(models.Model):
#     _name = "co.code.credit.note"
#     _inherit = 'co.abstract.codes'
#     _description = "Nota Crédito"
# 
#     _order = "code ASC, id ASC"
#     
# class CoCodeDebitNote(models.Model):
#     _name = "co.code.debit.note"
#     _inherit = 'co.abstract.codes'
#     _description = "Nota Débito"
# 
#     _order = "code ASC, id ASC"
# 
# class CoCodeEvent(models.Model):
#     _name = "co.code.event"
#     _inherit = 'co.abstract.codes'
#     _description = "Tipos de eventos"
# 
#     _order = "code ASC, id ASC"


class CoCodeIdentifier(models.Model):
    _inherit = "co.code.identifier"
    
    @api.model
    def update_saphety_codes(self):
        codes = self.env['co.saphety'].get_co_codes('v2/dataelements/identificationdocumenttypes')
        self.check_saphety_code(codes)
    
    @api.model
    def get_selection(self):
        res=[]
        datas=self.search([('active', '=', True),('saphety','=',True)])
        if datas:
            res = [(data.code,data.name) for data in datas]
        return res

class CoCodeTax(models.Model):
    _inherit = 'co.code.tax'
 
    @api.model
    def update_saphety_codes(self):
        codes = self.env['co.saphety'].get_co_codes('v2/dataelements/taxcategories')
        codes += self.env['co.saphety'].get_co_codes('v2/dataelements/withholdingtaxes')
        self.check_saphety_code(codes)
    
    @api.model
    def get_selection(self):
        res=[]
        datas=self.search([('active', '=', True),('saphety','=',True)])
        if datas:
            res = [(data.code,data.name) for data in datas]
        return res


class CoCodeAdditionalAccount(models.Model):
    _inherit = "co.code.additional.account"

    @api.model
    def update_saphety_codes(self):
        codes = self.env['co.saphety'].get_co_codes('v2/dataelements/legaltypes')
        self.check_saphety_code(codes)
    
    @api.model
    def get_selection(self):
        res=[]
        datas=self.search([('active', '=', True),('saphety','=',True)])
        if datas:
            res = [(data.code,data.name) for data in datas]
        return res

class CoCodeTaxLevel(models.Model):
    _inherit = "co.code.tax.level"
    
    @api.model
    def update_saphety_codes(self):
        codes = self.env['co.saphety'].get_co_codes('v2/dataelements/fiscalregimes')
        self.check_saphety_code(codes)
    
    @api.model
    def get_selection(self):
        res=[]
        datas=self.search([('active', '=', True),('saphety','=',True)])
        if datas:
            res = [(data.code,data.name) for data in datas]
        return res

# class CoCodeCreditNoteCode(models.Model):
#     _name = "co.code.credit.note.code"
#     _inherit = 'co.abstract.codes'
#     _description = "Correccion Notas crédito"
# 
#     _order = "code ASC, id ASC"
# 
# class CoCodeDebitNoteCode(models.Model):
#     _name = "co.code.debit.note.code"
#     _inherit = 'co.abstract.codes'
#     _description = "Correción para Notas débito"
# 
#     _order = "code ASC, id ASC"


class CoCodeTaxLevelCode(models.Model):
    _inherit = "co.code.tax.level.code"
    
    @api.model
    def update_saphety_codes(self):
        codes = self.env['co.saphety'].get_co_codes('v2/dataelements/responsabilitytypes')
        self.check_saphety_code(codes)
    
    @api.model
    def get_selection(self):
        res=[]
        datas=self.search([('active', '=', True),('saphety','=',True)])
        if datas:
            res = [(data.code,data.name) for data in datas]
        return res

# class CoCodeResponseCode(models.Model):
#     _name = "co.code.response.code"
#     _inherit = 'co.abstract.codes'
#     _description = "Eventos de un Documento Electrónico"
# 
#     _order = "code ASC, id ASC"

class CoCodePaymentMeans(models.Model):
    _inherit = "co.code.payment.means"

    @api.model
    def update_saphety_codes(self):
        codes = self.env['co.saphety'].get_co_codes('v2/dataelements/paymentmeansmeans')
        self.check_saphety_code(codes)

    @api.model
    def get_selection(self):
        res=[]
        datas=self.search([('active', '=', True),('saphety','=',True)])
        if datas:
            res = [(data.code,data.name) for data in datas]
        return res

class CoCodePaymentMeansCode(models.Model):
    _inherit =  "co.code.payment.means.code"
    
    @api.model
    def update_saphety_codes(self):
        codes = self.env['co.saphety'].get_co_codes('v2/dataelements/paymentmeanscode')
        self.check_saphety_code(codes)
    
    @api.model
    def get_selection(self):
        res=[]
        datas=self.search([('active', '=', True),('saphety','=',True)])
        if datas:
            res = [(data.code,data.name) for data in datas]
        return res
    
# class CoCodeProductTypeCode(models.Model):
#     _name = "co.code.product.type.code"
#     _inherit = 'co.abstract.codes'
#     _description = "Productos"
#     
#     agency_code = fields.Char("Agency Code")
#     
#     _order = "code ASC, id ASC"

class CoCodeProductCode(models.Model):
    _inherit = 'co.code.product'
    
    @api.model
    def update_saphety_codes(self):
        codes = self.env['co.saphety'].get_co_codes('v2/dataelements/unitsofmeasure')
        self.check_saphety_code(codes)
    
    @api.model
    def get_selection(self):
        res=[]
        datas=self.search([('active', '=', True),('saphety','=',True)])
        if datas:
            res = [(data.code,data.name) for data in datas]
        return res
    
 
class CoCodeResponsibility(models.Model):
    _inherit = "co.code.responsibility"
    
    @api.model
    def update_saphety_codes(self):
        codes = self.env['co.saphety'].get_co_codes('v2/dataelements/incoterms')
        self.check_saphety_code(codes)
    
    @api.model
    def get_selection(self):
        res=[]
        datas=self.search([('active', '=', True),('saphety','=',True)])
        if datas:
            res = [(data.code,data.name) for data in datas]
        return res
 
# class CoCodeDiscount(models.Model):
#     _name = "co.code.discount"
#     _inherit = 'co.abstract.codes'
#     _description = "Descuento"
#         
#     _order = "code ASC, id ASC"
# 
# 
# class CoCodeReferencePrice(models.Model):
#     _name = "co.code.reference.price"
#     _inherit = 'co.abstract.codes'
#     _description = "Precios de referencia"
#         
#     _order = "code ASC, id ASC"
# 
# class CoCodeRejet(models.Model):
#     _name = "co.code.rejet"
#     _inherit = 'co.abstract.codes'
#     _description = "Descuento"
#         
#     _order = "code ASC, id ASC"


