# -*- coding: utf-8 -*-
{
    'name': "Colombian toponyms",

    'summary': """Colombian toponyms""",

    'description': """
        Colombian toponyms
    """,

    'author': "Grupo YACCK",
    'website': "http://www.grupoyacck.com",

    'category': 'Localization/Toponyms',
    'version': '0.1',

    'depends': ['base', 'l10n_co', 'base_address_city'],

    'data': [
        'data/res_country_data.xml',
        'data/res.country.state.csv',
        'data/res.city.csv',
        'views/res_partner_view.xml',
    ],
}
