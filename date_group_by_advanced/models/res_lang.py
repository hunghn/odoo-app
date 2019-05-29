# -*- coding: utf-8 -*-
# Part of The Gok. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResLang(models.Model):
    _inherit = "res.lang"

    day_format = fields.Char(string="Day Format", default="dd MMM yyyy")
    week_format = fields.Char(string="Week Format", default="'W'w YYYY")
    month_format = fields.Char(string="Month Format", default="MMMM yyyy")
    quarter_format = fields.Char(string="Quarter Format", default="QQQ yyyy")
    year_format = fields.Char(string="Year Format", default="yyyy")
    format_type = fields.Selection(
        string="Format Type",
        selection=[('day', 'By Day'),
                   ('week', 'By Week'),
                   ('month', 'By Month'),
                   ('quarter', 'By Quarter'),
                   ('year', 'By Year')],
        default='month')
