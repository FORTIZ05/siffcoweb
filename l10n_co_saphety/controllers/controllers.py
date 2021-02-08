# -*- coding: utf-8 -*-
# from odoo import http


# class L10nCoSaphety(http.Controller):
#     @http.route('/l10n_co_saphety/l10n_co_saphety/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_co_saphety/l10n_co_saphety/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_co_saphety.listing', {
#             'root': '/l10n_co_saphety/l10n_co_saphety',
#             'objects': http.request.env['l10n_co_saphety.l10n_co_saphety'].search([]),
#         })

#     @http.route('/l10n_co_saphety/l10n_co_saphety/objects/<model("l10n_co_saphety.l10n_co_saphety"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_co_saphety.object', {
#             'object': obj
#         })
