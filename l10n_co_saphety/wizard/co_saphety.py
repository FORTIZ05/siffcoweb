import logging

import requests

from odoo import models, fields, _
from odoo.exceptions import ValidationError
import json
from datetime import datetime, timedelta
from base64 import decodestring
_log = logging.getLogger(__name__)

IDENTIFICATION_TYPES = {
    # Revisar
    'civil_registration': 'CivilRegistry',
    'id_document': 'IdentityCard',
    'id_card': 'CitizenshipCard',
    'foreign_id_card': 'ForeignerCard',
    'external_id': 'ForeignerIdentification',
    'rut': 'NIT',
    'passport': 'Passport',
    'foreign_id_card': 'ForeignIdentificationDocument',
    # '':'ForeignNIT',
    # '':'NUIP',

}

INVERSE_IDENTIFICATION_TYPES = {
    # Revisar
    'CivilRegistry':'civil_registration',
    'IdentityCard': 'id_document',
    'CitizenshipCard': 'id_card',
    'ForeignerCard': 'foreign_id_card',
    'ForeignerIdentification': 'external_id',
    'NIT': 'rut',
    'Passport': 'passport',
    'ForeignIdentificationDocument': 'foreign_id_card',
    # '':'ForeignNIT',
    # '':'NUIP',

}

class CoSaphety(models.AbstractModel):
    _name = 'co.saphety'
    _description = "Colombian Electronic Invoice using Saphety"

    # -----------------------------------------------------
    # Access Methods
    # -----------------------------------------------------

    def get_api_url(self):
        ConfigParamEnv = self.env['ir.config_parameter'].sudo()
        url = ConfigParamEnv.get_param('l10n_co_saphety.saphety_mode')
        return url

    @staticmethod
    def _process_response(response):
        res = {}
        try:
            res = response.json()
        except Exception:
            return {}
        return res
        
    
    def get_co_codes(self, code_url):
        url = f'{self.get_api_url()}/{code_url}'
        ResultData = []
        try:
            response = requests.get(url)
            
            response_data = self._process_response(response)
            ResultData = response_data.get('ResultData', {})
        except Exception:
            pass
        return ResultData

    @staticmethod
    def get_session():
        session = requests.session()
        session.proxies = {
            "http": False,
            "https": False,
        }
        return session

    def get_token(self, invoice=False):
        ConfigParamEnv = self.env['ir.config_parameter'].sudo()

        url = f'{self.get_api_url()}/v2/auth/gettoken'

        session = self.get_session()
        response = session.post(url, json={
            'username': ConfigParamEnv.get_param('l10n_co_saphety.saphety_username'),
            'password': ConfigParamEnv.get_param('l10n_co_saphety.saphety_password'),
            'virtual_operator': ConfigParamEnv.get_param('l10n_co_saphety.saphety_virtual_operator')
        })
        res = self._process_response(response)
        if not res.get('IsValid') and invoice:
            invoice.message_post(body=_('There was a problem getting the token.<br/>%s')%json.dumps(res, indent=4))
            return False
        if not res.get('IsValid') and not invoice:
            raise(json.dumps(res, indent=4))
        token = res.get('ResultData', {}).get('access_token')
        return token


    def get_all_series(self):
        ConfigParamEnv = self.env['ir.config_parameter'].sudo()
        virtual_operator = ConfigParamEnv.get_param('l10n_co_saphety.saphety_virtual_operator')
        company_key = self.env.user.company_id.saphety_key

        url = f"{self.get_api_url()}/v2/{virtual_operator}/companies/{company_key}/series/getall"
        token = self.get_token() #.get('ResultData', {}).get('access_token')
        session = self.get_session()
        response = session.get(url,
                               headers={
                                   'Authorization': f'Bearer {token}'
                               })
        res = response.json()
        if not res.get('IsValid'):
            raise ValidationError(json.dumps(res, indent=4))
        return res.get('ResultData', [])
        

    # -----------------------------------------------------
    # Json Methods
    # -----------------------------------------------------
    def get_payment_means(self, invoice_id):
        vals = {}
        vals['Code'] = invoice_id.co_payment_means_code
        vals['Mean'] = invoice_id.co_payment_means 
        #vals['DueDate'] = fields.Date.to_string(invoice_id.invoice_date_due)
        return [vals]

    def get_company(self, company_id, user_id = False):
        partner_id = company_id.partner_id
        # Duda
        type = IDENTIFICATION_TYPES.get(partner_id.l10n_co_document_type, False)
        if partner_id.l10n_co_document_type and not type:
            raise ValidationError(_("Identification document not supported"))
        if partner_id.l10n_co_document_type == 'rut' :
            co_vat = partner_id.vat.replace('-','').strip()
            if len(co_vat) == 10:
                l10n_co_verification_code =  co_vat[-1] #partner_id.l10n_co_verification_code
                vat = co_vat[:-1]
            else:
                l10n_co_verification_code = partner_id.l10n_co_verification_code
                vat = partner_id.vat
            #l10n_co_verification_code =  partner_id.vat[-1] #partner_id.l10n_co_verification_code
            #vat = partner_id.vat[:-1]
        else:
            l10n_co_verification_code = partner_id.l10n_co_verification_code
            vat = partner_id.vat
        
        vals = {
            "Identification": {
                "DocumentNumber": vat or '',
                "DocumentType": type,
                "CountryCode": partner_id.country_id.code,
                "CheckDigit": l10n_co_verification_code or ''
            }
        }
        if user_id:
            vals.update({'DocumentContacts':[{
                    'Name': user_id.name,
                    'Email': user_id.email,
                    'Type':'SellerContact'
                }]})
        return vals

    def get_exchange_rate(self, invoice_id):
        vals = {}
        if invoice_id.currency_id.name != 'COP':
            rate =  invoice_id.currency_id._convert(1, self.env.ref('base.COP'), invoice_id.company_id, date=invoice_id.invoice_date)
            vals['PaymentExchangeRate'] = {
                    "OriginCurrency": invoice_id.currency_id.name ,
                    "DestinyCurrency": 'COP',
                    'Rate': rate,
                    "Date":invoice_id.invoice_date.strftime("%Y-%m-%d")
                }
        return vals
            
    def get_partner(self, partner_id):
        type = IDENTIFICATION_TYPES.get(partner_id.l10n_co_document_type, False)
        if partner_id.l10n_co_document_type and not type:
            raise ValidationError(_("Identification document not supported"))
        if partner_id.l10n_co_document_type == 'rut' :
            co_vat = partner_id.vat.replace('-','').strip()
            if len(co_vat) == 10:
                l10n_co_verification_code =  co_vat[-1] #partner_id.l10n_co_verification_code
                vat = co_vat[:-1]
            else:
                l10n_co_verification_code = partner_id.l10n_co_verification_code
                vat = partner_id.vat
        else:
            l10n_co_verification_code = partner_id.l10n_co_verification_code
            vat = partner_id.vat
        co_tax_level_codes = []
        for co_tax_level_code in partner_id.co_tax_level_code_ids:
            co_tax_level_codes.append(co_tax_level_code.code)
        vals = {
            "LegalType": partner_id.co_legal_type,
            "Email": partner_id.email,
            "TaxScheme": partner_id.co_tax_level,
            "ResponsabilityTypes": co_tax_level_codes,
            "Name": partner_id.name,
            }
        address = {}
        if partner_id.country_id.code == 'CO':
            address['DepartmentCode'] = partner_id.state_id.co_code
            address['CityCode'] = partner_id.city_id.co_code
        else:
            address['DepartmentName'] = partner_id.state_id.name
            address['CityName'] = partner_id.city
        address['AddressLine'] = partner_id.street
        address['Country'] = partner_id.country_id.code
        address['PostalCode'] = partner_id.zip or None
        vals['Address'] = address
        identification = {
                "DocumentNumber": vat,
                "DocumentType": type,
                "CountryCode": partner_id.country_id.code,
            }
        if partner_id.l10n_co_document_type == 'rut':
            identification["CheckDigit"] = l10n_co_verification_code
        vals["Identification"]= identification
        if partner_id.company_type == 'person':
            vals["Person"] = {
                "FirstName": partner_id.co_first_name or '',
                "MiddleName": partner_id.co_middle_name or '',
                "FamilyName": partner_id.co_family_name or ''
                }
        return vals
        
    def get_lines(self, line_ids):
        lines = []
        number = 1
        round_qty = line_ids and line_ids[0].move_id.currency_id.decimal_places or 2
        for line in line_ids.filtered(lambda s: s.product_id.co_product_type==False or s.product_id.co_product_type in ['general']):
            values = {
                    'price_unit':line.price_unit, 
                    'quantity': line.quantity, 
                    'discount': line.discount,
                    'currency':line.currency_id,
                    'product':line.product_id,
                    'partner':line.partner_id,
                    'taxes':line.tax_ids,
                    'move_type':line.move_id.type,
                    }
            vals = {}
            vals['Number']=number
            number+=1
            vals['Quantity'] = line.quantity
            values.update({'quantity':1.0, 'discount':0.0})            
            unit_prices = line._get_price_total_and_subtotal_model(**values)
            values.update({'quantity':line.quantity, 'taxes':line.tax_ids.filtered(lambda s: s.co_tax_type_id.code not in ['RETEFUENTE', 'RETEIVA', 'RETEICA']),
                           'discount': line.discount})
            total_prices = line._get_price_total_and_subtotal_model(**values)
            vals['QuantityUnitOfMeasure'] = line.product_uom_id.co_unit_code or "NIU"
            vals['UnitPrice'] = unit_prices.get('price_subtotal')
            vals['NetAmount'] = total_prices.get('price_subtotal')
            
            values.update({'discount':0.0})
            total_prices_discount = line._get_price_total_and_subtotal_model(**values)
            
            vals['GrossAmount'] = total_prices_discount.get('price_subtotal')
            item = {}
            item["Description"] = line.name
            if line.product_id.barcode:
                item["gtin"] = line.product_id.barcode
            if line.product_id.default_code:
                item['BuyerItemIdentification'] = line.product_id.default_code
            if line.product_id.product_brand_id:
                item['BrandName'] = line.product_id.product_brand_id.name
            if line.move_id.co_saphety_mandate_id and line.move_id.co_operation_type == '11':
                identification = {}
                vat = False
                if line.move_id.co_saphety_mandate_id.l10n_co_document_type == 'rut' :
                    co_vat = line.move_id.co_saphety_mandate_id.vat.replace('-','').strip()
                    if len(co_vat) == 10:
                        l10n_co_verification_code =  co_vat[-1] #partner_id.l10n_co_verification_code
                        vat = co_vat[:-1]
                    else:
                        l10n_co_verification_code = partner_id.l10n_co_verification_code
                        vat = partner_id.vat
                else:
                    vat = line.move_id.co_saphety_mandate_id.vat
                identification['DocumentNumber'] = vat
                type = IDENTIFICATION_TYPES.get(line.move_id.co_saphety_mandate_id.l10n_co_document_type, False)
                identification['DocumentType'] = type
                identification['CountryCode'] = line.move_id.co_saphety_mandate_id.country_id.code 
                identification['CheckDigit'] = len(line.move_id.co_saphety_mandate_id.vat) == 10 and line.move_id.co_saphety_mandate_id.vat[-1] or line.move_id.co_saphety_mandate_id.l10n_co_verification_code
                item['MandatedAgent'] = {'Identification': identification}
            # Verificar ModelName
            
            vals['Item'] = item
            taxes = line._get_co_all_taxes()
            tax_vals = {}
            withholding_taxes = {}
            taxs = []
            holding_taxs = []
            for tax in taxes.get('taxes', []):
                tax_id = tax_id = line.env['account.tax'].browse([tax.get('id')])
                if tax_id.co_tax_type_id.code in ['RETEFUENTE', 'RETEIVA', 'RETEICA']:
                    withholding_taxes.setdefault(tax_id.co_tax_type_id.code, {'amount': 0.0, 'code':tax_id.co_tax_type_id.code})
                    tax_id = line.env['account.tax'].browse([tax.get('id')])
                    # Revisar el nombre del impuesto
                    val = {
                            'WithholdingTaxCategory':tax_id.co_tax_type_id.code,
                            'TaxPercentage':abs(tax_id.amount),
                            'TaxableAmount':tax.get('base', 0.0),
                            'TaxAmount':abs(tax.get('amount', 0.0)),
                            }
                    withholding_taxes[tax_id.co_tax_type_id.code]['amount']+= tax.get('amount', 0.0)
                    holding_taxs.append(val)
                    
                elif tax_id.co_tax_type_id.code in ['BOLSAS', 'IC', 'INCARBONO', 'INCOMBUSTIBLES', 'TIMBRE']:
                    tax_vals.setdefault(tax_id.co_tax_type_id.code, {'amount': 0.0, 'code':tax_id.co_tax_type_id.code})
                    tax_id = line.env['account.tax'].browse([tax.get('id')])
                    # Revisar el nombre del impuesto
                    val = {
                            'TaxCategory':tax_id.co_tax_type_id.code,
                            'TaxPercentage':0.0,
                            'PerUnitAmount': tax_id.amount,
                            'BaseUnitMeasure': tax.get('amount', 0.0)/tax_id.amount,
                            'BaseUnitMeasureUnitMeasure': 'A31',
                            'TaxAmount':tax.get('amount', 0.0),
                            }
                    tax_vals[tax_id.co_tax_type_id.code]['amount']+= tax.get('amount', 0.0)
                    taxs.append(val)
                else:
                    tax_vals.setdefault(tax_id.co_tax_type_id.code, {'amount': 0.0, 'code':tax_id.co_tax_type_id.code})
                    tax_id = line.env['account.tax'].browse([tax.get('id')])
                    # Revisar el nombre del impuesto
                    val = {
                            'TaxCategory':tax_id.co_tax_type_id.code,
                            'TaxPercentage':tax_id.amount,
                            'TaxableAmount':tax.get('base', 0.0),
                            'TaxAmount':tax.get('amount', 0.0),
                            }
                    tax_vals[tax_id.co_tax_type_id.code]['amount']+= tax.get('amount', 0.0)
                    taxs.append(val)
                    
            vals['TaxSubTotals'] = taxs
            if holding_taxs:
                vals['WithholdingTaxSubTotals'] = holding_taxs
            
            AllowanceCharges = []
            
            if line.discount>0.0:
                discount = total_prices_discount.get('price_subtotal') - total_prices.get('price_subtotal')
                AllowanceCharges.append({
                    "ChargeIndicator": "false",
                    "BaseAmount": total_prices_discount.get('price_subtotal'),
                    "ReasonCode": "02",
                    "Reason": "Descuento a nivel de linea",
                    "Amount": discount,
                    "Percentage": round(1-total_prices.get('price_subtotal')/total_prices_discount.get('price_subtotal'), 4),
                    "SequenceIndicator": "1"
                })
            if AllowanceCharges:
                vals['AllowanceCharges'] = AllowanceCharges
            taxes = []
            for code, tax in sorted(tax_vals.items()):
                val = {
                    "TaxCategory": code,
                    "TaxAmount": tax.get("amount")
                    }
                taxes.append(val)
            if withholding_taxes:
                holding_totaltaxs = []
                for code, tax in sorted(withholding_taxes.items()):
                    val = {
                        "WithholdingTaxCategory": code,
                        "TaxAmount": abs(tax.get("amount"))
                        }
                    holding_totaltaxs.append(val)
                vals['WithholdingTaxTotals'] = holding_totaltaxs
            vals['TaxTotals'] = taxes
                
            lines.append(vals)
            
        return lines
    
    def get_taxtotals(self, invoice_id):
        subtotals = []
        withholding_taxes = []
        taxes = invoice_id._compute_invoice_taxes_by_co_group()
        for id, tax in taxes:
            tax_id = invoice_id.env['account.tax'].browse([tax.get('tax_id')])
            # Revisar el nombre del impuesto
            if tax_id.co_tax_type_id.code in ['RETEFUENTE', 'RETEIVA', 'RETEICA']:
                val = {
                    'WithholdingTaxCategory':tax_id.co_tax_type_id.code,
                    'TaxAmount':abs(tax.get('amount', 0.0)),
                    'TaxableAmount':tax.get('base', 0.0),
                    'TaxPercentage':abs(tax_id.amount),
                    }
                withholding_taxes.append(val)
            elif tax_id.co_tax_type_id.code in ['BOLSAS', 'IC', 'INCARBONO', 'INCOMBUSTIBLES', 'TIMBRE']:
                val = {
                    'TaxCategory':tax_id.co_tax_type_id.code,
                    'TaxPercentage': 0.0, #,
                    'PerUnitAmount': tax_id.amount,
                    'BaseUnitMeasure': tax.get('amount', 0.0)/tax_id.amount,
                    'BaseUnitMeasureUnitMeasure': 'A31',
                    'TaxAmount':tax.get('amount', 0.0),
                    
                    }
                subtotals.append(val)
            else:
                val = {
                    'TaxCategory':tax_id.co_tax_type_id.code,
                    'TaxAmount':tax.get('amount', 0.0),
                    'TaxableAmount':tax.get('base', 0.0),
                    'TaxPercentage':abs(tax_id.amount),
                    }
                subtotals.append(val)
        taxes = invoice_id._compute_invoice_taxes_by_co_code()
        totals = []
        withholding_total_taxes = []
        rete_amount = 0.0
        for code, tax in taxes:
            if code not in ['RETEFUENTE', 'RETEIVA', 'RETEICA']:
                val = {
                    'TaxCategory':code,
                    'TaxAmount':tax.get('amount', 0.0),
                    }
                totals.append(val)
            else:
                rete_amount += abs(tax.get('amount', 0.0))
                val = {
                    'WithholdingTaxCategory':code,
                    'TaxAmount':abs(tax.get('amount', 0.0)),
                    }
                withholding_total_taxes.append(val)
        return rete_amount, {'TaxSubTotals':subtotals, 'TaxTotals':totals, 'WithholdingTaxSubTotals':withholding_taxes, 'WithholdingTaxTotals':withholding_total_taxes}
    
    def get_totals(self, invoice_id, rete_amount):
        pre_paid_total = abs(sum(invoice_id.invoice_line_ids.filtered(lambda s: s.product_id.co_product_type in ['pre_payment']).mapped('price_total')))
        discount_total = abs(sum(invoice_id.invoice_line_ids.filtered(lambda s: s.product_id.co_product_type in ['discount']).mapped('price_total')))
        charge_total = sum(invoice_id.invoice_line_ids.filtered(lambda s: s.product_id.co_product_type in ['charge']).mapped('price_total'))
        vals = {}
        vals['GrossAmount'] = invoice_id.amount_untaxed + pre_paid_total + discount_total - charge_total
        vals['TotalBillableAmount'] = invoice_id.amount_total + rete_amount + pre_paid_total + discount_total - charge_total
        vals['PayableAmount'] = invoice_id.amount_total + rete_amount
        vals['TaxableAmount'] = invoice_id.amount_untaxed  + pre_paid_total + discount_total - charge_total
        vals['AllowancesTotalAmount'] = discount_total
        vals['ChargesTotalAmount'] = charge_total
        vals['PrePaidTotalAmount'] = pre_paid_total
        
        line_ids = invoice_id.invoice_line_ids.filtered(lambda s: s.product_id.co_product_type in ['charge', 'discount'])
        discount_charges = []
        sequence = 1
        for line_id in line_ids:
            if line_id.product_id.co_product_type in ['discount']:
                discount_charges.append({
                    "ChargeIndicator": "false",
                    "BaseAmount": abs(vals['GrossAmount']),
                    "ReasonCode": "00",
                    "Reason": "Descuento a nivel de Factura",
                    "Amount": abs(line_id.price_total),
                    "Percentage": round(abs(line_id.price_total)*100/vals['GrossAmount'], 4),
                    "SequenceIndicator": sequence
                })
                sequence+=1
            elif line_id.product_id.co_product_type in ['charge']:
                discount_charges.append({
                    "ChargeIndicator": "true",
                    "BaseAmount": abs(vals['GrossAmount']),
                    "ReasonCode": "00",
                    "Reason": "Cargo a nivel de Factura",
                    "Amount": abs(line_id.price_total),
                    "Percentage": round(abs(line_id.price_total)*100/vals['GrossAmount'], 4),
                    "SequenceIndicator": sequence
                })
                sequence+=1
        return {'Total': vals, 'AllowanceCharges': discount_charges} 
    
    def get_references(self, invoice_id):
        vals = {}
        references = []
        if invoice_id.co_credit_note_code:
            vals["ReasonCredit"]= invoice_id.co_credit_note_code
        if invoice_id.co_debit_note_code:
            vals["ReasonDebit"]= invoice_id.co_debit_note_code
        if invoice_id.reversed_entry_id:
            references.append({
                  "DocumentReferred": invoice_id.reversed_entry_id.name,
                  "IssueDate": invoice_id.reversed_entry_id.co_saphety_invoice_date.strftime("%Y-%m-%dT%H:%M:%S"),
                  "Type": "InvoiceReference",
                  "DocumentReferredCUFE": invoice_id.reversed_entry_id.co_saphety_cufe
                })
        if invoice_id.invoice_line_ids.mapped('sale_line_ids'):
            for order_id in invoice_id.invoice_line_ids.mapped('sale_line_ids').mapped('order_id').filtered(lambda s: s.state != 'cancel'):
                references.append(
                    {
                        "DocumentReferred": order_id.client_order_ref or order_id.name,
                        "IssueDate": (order_id.date_order - timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S"),
                        "Type": "OrderReference"
                        }
                    )
                for picking_id in order_id.picking_ids:
                    send_date =  picking_id.date_done or picking_id.scheduled_date
                    references.append(
                        {
                            "DocumentReferred": picking_id.name,
                            "IssueDate": (send_date - timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S"),
                            "Type": "DespatchReference"
                            }
                        )
        if references:
            vals['DocumentReferences'] = references
        return vals
    
    def get_prepaid_payments(self, invoice_id):
        line_ids = invoice_id.invoice_line_ids.filtered(lambda s: s.product_id.co_product_type in ['pre_payment'])
        payments = []
        vals = {}
        for line in line_ids:
            invoice_line = line.sale_line_ids.mapped('invoice_lines').filtered(lambda s: s.move_id.id !=invoice_id.id)
            if invoice_line:
                payments.append({'PaidDate':invoice_line[0].move_id.invoice_date.strftime("%Y-%m-%d"),
                                 'PaidAmount':abs(line.price_total)})
            else:
                payments.append({'PaidDate':invoice_id.invoice_date.strftime("%Y-%m-%d"),
                                 'PaidAmount':abs(line.price_total)})
        if payments:
            vals['PrepaidPayments'] = payments
        return vals
    
    def get_attachment(self, invoice_id):
        attach_ids = self.env['ir.attachment'].search([('res_id','=',invoice_id.id),('res_model','=','account.move'),('co_saphety_send','=',False)])
        res = []
        for attach_id in attach_ids:
            if attach_id.file_size <= 3145728 and '.json' not in attach_id.name:
                vals = {
                    'ContentType': attach_id.mimetype,
                    'Filename': attach_id.name,
                    'Content': str(attach_id.datas, 'utf-8')
                    }
                res.append(vals)
        return {'Attachments':res}
    
    def get_document(self, invoice_id):
        vals = {}
        if invoice_id.type == 'out_refund':
            if invoice_id.journal_id.refund_sequence:
                vals["SeriePrefix"] = invoice_id.journal_id.co_saphety_credit_note.prefix
                vals["SerieExternalKey"] = invoice_id.journal_id.co_saphety_credit_note.external_key
        
            else:
                vals["SeriePrefix"] = invoice_id.journal_id.co_saphety_invoice.prefix
                vals["SerieExternalKey"] = invoice_id.journal_id.co_saphety_invoice.external_key
        
        else:
            vals["SeriePrefix"] = invoice_id.journal_id.co_saphety_invoice.prefix
            vals["SerieExternalKey"] = invoice_id.journal_id.co_saphety_invoice.external_key
        
        vals["SerieNumber"] = invoice_id.name.split('-')[-1]
        vals["IssueDate"] = invoice_id.co_saphety_invoice_date.strftime("%Y-%m-%dT%H:%M:%S")
        vals["DueDate"] = "%sT23:59:59" % fields.Date.to_string(invoice_id.invoice_date_due)
        vals["DeliveryDate"] = invoice_id.co_saphety_invoice_date.strftime("%Y-%m-%dT%H:%M:%S")
        vals["Currency"] = invoice_id.currency_id.name
        vals["OperationType"] = invoice_id.co_operation_type
        vals["CorrelationDocumentId"] = "%s/%s/%s" %(invoice_id.partner_id.vat, invoice_id.name, fields.Datetime.to_string(fields.Datetime.context_timestamp(self, datetime.now())))
        vals["PaymentMeans"] = self.get_payment_means(invoice_id)
        vals["IssuerParty"] = self.get_company(invoice_id.company_id, invoice_id.invoice_user_id)
        vals.update(self.get_exchange_rate(invoice_id))
        vals["CustomerParty"] = self.get_partner(invoice_id.partner_id)
        vals['Lines'] = self.get_lines(invoice_id.invoice_line_ids)
        rete_amount, tax_vals = self.get_taxtotals(invoice_id)
        vals.update(tax_vals)
        
        vals.update(self.get_prepaid_payments(invoice_id))
        vals.update(self.get_totals(invoice_id, rete_amount))
        vals.update(self.get_references(invoice_id))
        vals['CustomFields'] = [{"Key": "VALOR_LETRAS", "Value": invoice_id.currency_id.amount_to_text(vals.get('Total', {}).get('PayableAmount', 0.0))}]
        notes = ["SON: %s" % invoice_id.currency_id.amount_to_text(vals.get('Total', {}).get('PayableAmount', 0.0))]
        #notes = []
        if invoice_id.company_id.report_footer:
            notes+=["%s" % invoice_id.company_id.report_footer]
        if invoice_id.narration:
            notes+=["%s" % invoice_id.narration]
        vals['notes'] = [" | ".join(notes)]
        vals.update(self.get_attachment(invoice_id))
        _log.info(json.dumps(vals, indent=4))
        return vals #json.dumps(vals)
    
    def send_documents(self, invoice_id):
        ConfigParamEnv = self.env['ir.config_parameter'].sudo()
        virtual_operator = ConfigParamEnv.get_param('l10n_co_saphety.saphety_virtual_operator')
        company_key = invoice_id.company_id.saphety_key
        
        if invoice_id.type in ['out_invoice']:
            if invoice_id.co_invoice_code == '92':
                url = f"{self.get_api_url()}/v2/{virtual_operator}/outbounddocuments/debitNote"
            else:
                url = f"{self.get_api_url()}/v2/{virtual_operator}/outbounddocuments/salesInvoice"
        elif invoice_id.type in ['out_refund']:
            url = f"{self.get_api_url()}/v2/{virtual_operator}/outbounddocuments/creditNote"
        else:
            return False
        token = self.get_token(invoice_id)
        if not token:
            return False
        vals = self.get_document(invoice_id)
        session = self.get_session()
        response = session.post(url,
                               headers={
                                   'Content-Type': 'application/json',
                                   'Authorization': f'Bearer {token}'
                               }, json= vals)
        res = self._process_response(response)
        
        _log.info(json.dumps(res, indent=4))
        if not res.get('IsValid'):
            invoice_id.co_events = '04'
            invoice_id.message_post(body=_('There was a problem sending the document.<br/>%s') % json.dumps(res, indent=4).replace("\n", '<br/>'),
                              attachments=[("%s.json" % invoice_id.name, json.dumps(vals, indent=4))])
        else:
            warnings = res.get("warnings") and json.dumps(res.get('warnings'), indent=4) or ''
            errors = res.get("errors") and json.dumps(res.get('errors'), indent=4) or ''
            invoice_id.co_saphety_id = res.get('ResultData', {}).get("Id")
            invoice_id.co_saphety_correlation = res.get('ResultData', {}).get("CorrelationDocumentId")
            attach_ids = self.env['ir.attachment'].search([('res_id','=',invoice_id.id),('res_model','=','account.move'),('co_saphety_send','=',False)])
            invoice_id.co_events = '02'
            for attach_id in attach_ids:
                if attach_id.file_size <= 3145728:
                    attach_id.co_saphety_send= True
            if res.get('ResultData', {}).get('Content'):
                invoice_id.message_post(body=_('Sending the electronic document succeeded.<br/>%s<br/>%s') %(warnings.replace("\n", '<br/>'), errors.replace("\n", '<br/>')),
                                 attachments=[("%s.xml" % invoice_id.name, decodestring(res.get('ResultData', {}).get('Content').encode('utf-8')))])
            else:
                invoice_id.message_post(body=_('Sending the electronic document succeeded.<br/>%s<br/>%s')%(warnings, errors))
        return True

    def check_document_status(self, invoice_id):
        #if invoice_id.co_saphety_cufe:
        #    return True
        ConfigParamEnv = self.env['ir.config_parameter'].sudo()
        virtual_operator = ConfigParamEnv.get_param('l10n_co_saphety.saphety_virtual_operator')
        company_key = invoice_id.company_id.saphety_key
        document_id = invoice_id.co_saphety_id
        if not document_id:
            invoice_id.message_post(body=_('Document is without ID'))
            return False
        url = f"{self.get_api_url()}/v2/{virtual_operator}/outbounddocuments/{document_id}"
        token = self.get_token(invoice_id)
        if not token:
            return False
        vals = {}
        session = self.get_session()
        response = session.get(url,
                               headers={
                                   'Content-Type': 'application/json',
                                   'Authorization': f'Bearer {token}'
                               }, json= vals)
        res = self._process_response(response)
        
        _log.info(json.dumps(res, indent=4))
        if not res.get('IsValid'):
            if not invoice_id.env.context.get("co_no_validate"):
                invoice_id.message_post(body=_('There was a problem consult the document.<br/>%s') % json.dumps(res, indent=4).replace("\n", '<br/>'))
        else:
            warnings = res.get("warnings") and json.dumps(res.get('warnings').replace("\n", '<br/>'), indent=4) or ''
            errors = res.get("errors") and json.dumps(res.get('errors').replace("\n", '<br/>'), indent=4) or ''
            if res.get('ResultData', {}).get("DocumentStatus", '') == 'Certified':
                invoice_id.co_events = '030'
            elif res.get('ResultData', {}).get("DocumentStatus", '') == 'Accepted':
                invoice_id.co_events = '033'
            elif res.get('ResultData', {}).get("DocumentStatus", '') == 'Rejected':
                invoice_id.co_events = '031'
                if invoice_id.type in ['out_invoice']:
                    move_id = self.env['account.move'].search([('reversed_entry_id','=',invoice_id.id),('co_credit_note_code','=','2')], limit =1)
                    if not move_id:
                        context = {}
                        context['active_id'] = invoice_id.id
                        context['active_ids'] = invoice_id.id
                        context['default_co_credit_note_code'] = '2'
                        #context['default_co_operation_type'] = '20'
                        values = {}
                        values['refund_method'] = 'refund'
                        values['residual'] = invoice_id.amount_residual
                        values['currency_id'] = invoice_id.currency_id
                        values['move_type'] = invoice_id.type
                        values['move_id'] = invoice_id.id
                        values['reason'] = "Anulacion"
                        values['co_credit_note_code'] = '2'
                        values['date'] = fields.Date.context_today(self)
                        wizard_id = self.env['account.move.reversal'].with_context(**context).create(values)
                        data = wizard_id.reverse_moves()
                else:
                    context = {}
                    context['co_saphety_refund'] = True
                    invoice_id.with_context(**context).button_draft()
                    invoice_id.with_context(**context).button_cancel()
                    
            if not invoice_id.co_saphety_cufe:
                invoice_id.co_saphety_cufe = res.get('ResultData', {}).get("Cufe")
                if res.get('ResultData', {}).get('Cufe'):
                    invoice_id.message_post(body=_('CUFE: %s<br/>%s<br/>%s') %(res.get('ResultData', {}).get('Cufe'), warnings, errors))
        return True
    
    def get_document_pdf(self, invoice_id):
        ConfigParamEnv = self.env['ir.config_parameter'].sudo()
        virtual_operator = ConfigParamEnv.get_param('l10n_co_saphety.saphety_virtual_operator')
        company_key = invoice_id.company_id.saphety_key
        document_id = invoice_id.co_saphety_id
        if not document_id:
            invoice_id.message_post(body=_('Document is without ID'))
            return False
        url = f"{self.get_api_url()}/v2/{virtual_operator}/outbounddocuments/{document_id}/pdf"
        token = self.get_token(invoice_id)
        if not token:
            return False
        vals = {}
        session = self.get_session()
        response = session.get(url,
                               headers={
                                   'Content-Type': 'application/json',
                                   'Authorization': f'Bearer {token}'
                               }, json= vals)
        res = self._process_response(response)
        _log.info(json.dumps(res, indent=4))
        if not res.get('IsValid'):
            invoice_id.message_post(body=_('There was a problem consult the document.<br/>%s') % json.dumps(res, indent=4).replace("\n", '<br/>'))
        else:
            warnings = res.get("warnings") and json.dumps(res.get('warnings').replace("\n", '<br/>'), indent=4) or ''
            errors = res.get("errors") and json.dumps(res.get('errors').replace("\n", '<br/>'), indent=4) or ''
            if res.get('ResultData', {}).get('Content'):
                invoice_id.co_saphety_pdf = True
                invoice_id.message_post(body=_('%s<br/>%s') %(warnings, errors),
                                        attachments=[("%s.pdf" % invoice_id.name, decodestring(res.get('ResultData', {}).get('Content').encode('utf-8')))])
        return True
    
    def get_company_information(self, company_id):
        ConfigParamEnv = self.env['ir.config_parameter'].sudo()
        virtual_operator = ConfigParamEnv.get_param('l10n_co_saphety.saphety_virtual_operator')        
        url = f"{self.get_api_url()}/v2/{virtual_operator}/companies/search"
        token = self.get_token()
        vat = company_id.vat and len(company_id.vat)== 10 and company_id.vat[:9] or company_id.vat
        vals = { 
                    "Offset": "0", 
                    "NumberOfRecords": "20", 
                    "SortField": "-CreationDate",
                    "DocumentNumber": vat,
                }
        session = self.get_session()
        response = session.post(url,
                               headers={
                                   'Content-Type': 'application/json',
                                   'Authorization': f'Bearer {token}'
                               }, json= vals)
        res = self._process_response(response)
        
        _log.info(json.dumps(res, indent=4))
        
        if not res.get('IsValid'):
            raise ValidationError(_("There was a problem with your request check with the administrator"))
        else:
            if not res.get('ResultData'):
                raise ValidationError(_("Company not found"))
            else:
                result = res.get('ResultData')[0]
                company_id.saphety_key = result.get('Id')
                val = {}
                val['name'] = result.get('Name')
                #val['co_legal_type'] = result.get('LegalType')
                #doc_type = result.get('Identification', {}).ge('DocumentType', False)
                #val['l10n_co_document_type'] = doc_type and INVERSE_IDENTIFICATION_TYPES.get(doc_type,False) or False
                #val['name'] = result.get('Identification', {}).get('DocumentNumber',False)
                val['website'] = result.get('WebsiteUrl', False)
                val['email'] = result.get('Email', False)
                val['street'] = result.get('Address', {}).get('AddressLine',False)
                val['zip'] = result.get('CityCode')
                company_id.partner_id.write(val)
        return True
                
                
                
                
    


