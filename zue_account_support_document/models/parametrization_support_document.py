# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError
import time


class account_journal(models.Model):
    _inherit = 'account.journal'

    document_analyze = fields.Boolean(string='Reportar documento')


