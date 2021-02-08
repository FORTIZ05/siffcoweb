# -*- coding: utf-8 -*-
{
    'name': "Colombian Invoice",

    'summary': """
        Colombian Invoice""",

    'description': """
        Colombian Invoice
    """,

    'author': "Grupo YACCK",
    'website': "http://www.grupoyacck.com",

    'category': 'Uncategorized',
    'version': '0.2',
    'depends': [
        'account',
        'uom',
        'l10n_co',
        'l10n_co_codes',
        'l10n_co_toponyms',
    ],
    'data': [
        'data/res_currency_data.xml',
        'views/account_view.xml',
        'views/account_move_view.xml',
        'views/product_view.xml',
        #'views/currency_view.xml',
        'views/uom_view.xml',
        'views/res_partner_view.xml',
        'wizard/account_move_debit_view.xml',
        'wizard/account_move_reversal_view.xml'
    ],
}