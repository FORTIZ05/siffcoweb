# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CoCodeAmbient(models.Model):
    _name = "co.code.ambient"
    _inherit = 'co.abstract.codes'
    _description = "Ambiente"

    _order = "code ASC, id ASC"
    

class CoCodeDocument(models.Model):
    _name = "co.code.document"
    _inherit = 'co.abstract.codes'
    _description = "Tipo de Documento"

    _order = "code ASC, id ASC"

class CoCodeDocumentReference(models.Model):
    _name = "co.code.document.reference"
    _inherit = 'co.abstract.codes'
    _description = "Referencia a documentos no trib"

    _order = "code ASC, id ASC"

# Falta Referencia a documentos no trib

class CoCodeOperationType(models.Model):
    _name = "co.code.operation.type"
    _inherit = 'co.abstract.codes'
    _description = "Tipos de operación"

    _order = "code ASC, id ASC"

class CoCodeOperationTypeHealth(models.Model):
    _name = "co.code.operation.type.health"
    _inherit = 'co.abstract.codes'
    _description = "Tipos de operación Salud"

    _order = "code ASC, id ASC"

class CoCodeCreditNote(models.Model):
    _name = "co.code.credit.note"
    _inherit = 'co.abstract.codes'
    _description = "Nota Crédito"

    _order = "code ASC, id ASC"
    
class CoCodeDebitNote(models.Model):
    _name = "co.code.debit.note"
    _inherit = 'co.abstract.codes'
    _description = "Nota Débito"

    _order = "code ASC, id ASC"

class CoCodeEvent(models.Model):
    _name = "co.code.event"
    _inherit = 'co.abstract.codes'
    _description = "Tipos de eventos"

    _order = "code ASC, id ASC"


class CoCodeIdentifier(models.Model):
    _name = "co.code.identifier"
    _inherit = 'co.abstract.codes'
    _description = "Identificación fiscal"

    _order = "code ASC, id ASC"

class CoCodeTax(models.Model):
    _name = "co.code.tax"
    _inherit = 'co.abstract.codes'
    _description = "Tributos"

    _order = "code ASC, id ASC"

class CoCodeAdditionalAccount(models.Model):
    _name = "co.code.additional.account"
    _inherit = 'co.abstract.codes'
    _description = "Organización jurídica"

    _order = "code ASC, id ASC"

class CoCodeTaxLevel(models.Model):
    _name = "co.code.tax.level"
    _inherit = 'co.abstract.codes'
    _description = "Régimen Fiscal"

    _order = "code ASC, id ASC"

class CoCodeCreditNoteCode(models.Model):
    _name = "co.code.credit.note.code"
    _inherit = 'co.abstract.codes'
    _description = "Correccion Notas crédito"

    _order = "code ASC, id ASC"

class CoCodeDebitNoteCode(models.Model):
    _name = "co.code.debit.note.code"
    _inherit = 'co.abstract.codes'
    _description = "Correción para Notas débito"

    _order = "code ASC, id ASC"


class CoCodeTaxLevelCode(models.Model):
    _name = "co.code.tax.level.code"
    _inherit = 'co.abstract.codes'
    _description = "Responsabilidades fiscales"

    _order = "code ASC, id ASC"

class CoCodeResponseCode(models.Model):
    _name = "co.code.response.code"
    _inherit = 'co.abstract.codes'
    _description = "Eventos de un Documento Electrónico"

    _order = "code ASC, id ASC"

class CoCodePaymentMeans(models.Model):
    _name = "co.code.payment.means"
    _inherit = 'co.abstract.codes'
    _description = "Formas de Pago"

    _order = "code ASC, id ASC"


class CoCodePaymentMeansCode(models.Model):
    _name = "co.code.payment.means.code"
    _inherit = 'co.abstract.codes'
    _description = "Medios de Pago"

    _order = "code ASC, id ASC"

class CoCodeProductTypeCode(models.Model):
    _name = "co.code.product.type.code"
    _inherit = 'co.abstract.codes'
    _description = "Productos"
    
    agency_code = fields.Char("Agency Code")
    
    _order = "code ASC, id ASC"

class CoCodeProductCode(models.Model):
    _name = "co.code.product"
    _inherit = 'co.abstract.codes'
    _description = "Unidades de Cantidad"
        
    _order = "code ASC, id ASC"

class CoCodeResponsibility(models.Model):
    _name = "co.code.responsibility"
    _inherit = 'co.abstract.codes'
    _description = "Condiciones de entrega"
        
    _order = "code ASC, id ASC"

class CoCodeDiscount(models.Model):
    _name = "co.code.discount"
    _inherit = 'co.abstract.codes'
    _description = "Descuento"
        
    _order = "code ASC, id ASC"


class CoCodeReferencePrice(models.Model):
    _name = "co.code.reference.price"
    _inherit = 'co.abstract.codes'
    _description = "Precios de referencia"
        
    _order = "code ASC, id ASC"

class CoCodeRejet(models.Model):
    _name = "co.code.rejet"
    _inherit = 'co.abstract.codes'
    _description = "Descuento"
        
    _order = "code ASC, id ASC"


