# -*- coding: utf-8 -*-
# Part of The Gok. See LICENSE file for full copyright and licensing details.

import pytz
import datetime
import dateutil
from odoo import api, models


class BaseModelExtend(models.AbstractModel):
    _name = 'base.model.extend'
    models.BaseModel._navigation = 'id'

    @api.model_cr
    def _register_hook(self):
        '''
        Register method in BaseModel
        '''
        @api.model
        def _read_group_process_groupby(self, gb, query):
            """
            ###################################################################
            Overide function _read_group_process_groupby native in models ->
            BaseModel to update format date group.
            group_by: day with format in config language
            ###################################################################
            Helper method to collect important information about groupbys: raw
            field name, type, time information, qualified name, ...
            """
            split = gb.split(':')
            field_type = self._fields[split[0]].type
            gb_function = split[1] if len(split) == 2 else None
            temporal = field_type in ('date', 'datetime')
            tz_convert = field_type == 'datetime' and self._context.get(
                'tz') in pytz.all_timezones
            qualified_field = self._inherits_join_calc(
                self._table, split[0], query)

            # Get date format in config language
            date_format, type_format = self.env[
                'base.model.extend']._get_config_format_date(
                gb_function)
            if temporal:
                display_formats = {
                    # Careful with week/year formats:
                    #  - yyyy (lower) must always be used, *except* for
                    #  week+year formats
                    #  - YYYY (upper) must always be used for week+year format
                    #      e.g. 2006-01-01 is W52 2005 in some locales (de_DE),
                    #                         and W1 2006 for others
                    #
                    # Mixing both formats, e.g. 'MMM YYYY' would yield wrong
                    # results,
                    # such as 2006-01-01 being formatted as "January 2005" in
                    # some locales.
                    # Cfr: http://babel.pocoo.org/docs/dates/#date-fields
                    'day': date_format and date_format.get('day') or\
                    'dd/MM/yyyy',
                    'week': date_format and date_format.get('week') or\
                    "'W'w YYYY",  # w YYYY = ISO week-year
                    'month': date_format and date_format.get('month') or\
                    'MMMM yyyy',
                    'quarter': date_format and date_format.get('quarter') or\
                    'QQQ yyyy',
                    'year': date_format and date_format.get('year') or\
                    'yyyy',
                }
                time_intervals = {
                    'day': dateutil.relativedelta.relativedelta(days=1),
                    'week': datetime.timedelta(days=7),
                    'month': dateutil.relativedelta.relativedelta(months=1),
                    'quarter': dateutil.relativedelta.relativedelta(months=3),
                    'year': dateutil.relativedelta.relativedelta(years=1)
                }
                if tz_convert:
                    qualified_field = "timezone('%s', timezone('UTC',%s))" % (
                        self._context.get('tz', 'UTC'), qualified_field)
                qualified_field = "date_trunc('%s', %s)" % (
                    type_format, qualified_field)
            if field_type == 'boolean':
                qualified_field = "coalesce(%s,false)" % qualified_field

            return {
                'field': split[0],
                'groupby': gb,
                'type': field_type,
                'display_format': temporal and type_format and display_formats[
                    type_format] or None,
                'interval': time_intervals[
                    type_format] if temporal else None,
                'tz_convert': tz_convert,
                'qualified_field': qualified_field
            }

        # Assign method override
        models.BaseModel._read_group_process_groupby =\
            _read_group_process_groupby
        return super(BaseModelExtend, self)._register_hook()

    @api.model
    def _get_config_format_date(self, gb_function):
        """
        Get format base on language of user
        @param gb_function: this attribute has been set up in code xml of dev
        Its day, week, month, quarter or year.
        @return type_for, dictionary of format
        """
        # Get current user
        uid = self._uid or False
        user = uid and self.env['res.users'].browse(uid) or False
        if not user:
            return ({}, 'month')
        # Get current laguague set in user
        language = self.env['res.lang'].search(
            [('code', '=', user.lang)], limit=1)

        # Get group_by in code first, if it dont find we get in setting
        # language, if it dont setting we will get default month
        type_format = gb_function or (language and language.format_type) or\
            'month'

        return language and\
            ({'day': language.day_format,
              'week': language.week_format,
              'month': language.month_format,
              'quarter': language.quarter_format,
              'year': language.year_format}, type_format) or ({}, 'month')
