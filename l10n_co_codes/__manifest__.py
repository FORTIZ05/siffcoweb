# -*- coding: utf-8 -*-
{
    'name': "DIAN Codes",

    'summary': """
        Account, Invoice""",

    'description': """
        Elements, Attributes and Codes
    """,

    'author': "Grupo YACCK",
    'website': "http://www.grupoyacck.com",

    'category': 'Localization/Colombian',
    'version': '0.1',

    'depends': ['l10n_co'],

    # always loaded
    'data': [
        'security/co_codes_security.xml',
        'security/ir.model.access.csv',
        'data/co.code.additional.account.csv',
        'data/co.code.debit.note.csv',         
        'data/co.code.identifier.csv',          
        'data/co.code.reference.price.csv',  
        'data/co.code.tax.level.code.csv',
        'data/co.code.ambient.csv',             
        'data/co.code.discount.csv',
        'data/co.code.operation.type.csv',      
        'data/co.code.rejet.csv',            
        'data/co.code.tax.level.csv',
        'data/co.code.credit.note.code.csv',    
        'data/co.code.document.csv',
        'data/co.code.payment.means.csv',            
        'data/co.code.payment.means.code.csv',  
        'data/co.code.response.code.csv',
        'data/co.code.credit.note.csv',         
        'data/co.code.document.reference.csv',  
        'data/co.code.product.csv',             
        'data/co.code.responsibility.csv',
        'data/co.code.debit.note.code.csv',     
        'data/co.code.event.csv',               
        'data/co.code.product.type.code.csv',   
        'data/co.code.tax.csv',
        #'views/catalog_views.xml',
        #'views/catalog_menu.xml',
    ],
}