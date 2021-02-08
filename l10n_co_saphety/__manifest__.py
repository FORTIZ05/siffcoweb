# -*- coding: utf-8 -*-
{
    'name': "Saphety",

    'summary': """
        Saphety Electronic Invoice""",

    'description': """
        Saphety Electroni Invoice
    """,

    'author': "Grupo YACCK",
    'website': "http://www.grupoyacck.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['account', "l10n_co_invoice", "sale", "product_brand"],

    'data': [
        # security
        'security/ir.model.access.csv',
        # data
        'data/saphety_series_data.xml',
        'data/ir_cron_data.xml',
        # views
        'views/res_config_settings_views.xml',
        'views/co_saphety_series_views.xml',
        'views/res_company_views.xml',
        'views/menu.xml',
        'views/account_view.xml',
        'views/account_move_view.xml',
        # wizard
        'wizard/co_saphety_wizard_view.xml'
    ],

}
