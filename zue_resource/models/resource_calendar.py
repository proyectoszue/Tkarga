from odoo import models, fields, api

class resource_calendar(models.Model):
    _inherit = 'resource.calendar'

    type_working_schedule = fields.Selection([
        ('employees', 'Empleados'),
        ('tasks', 'Tareas Proyectos'),
        ('other', 'Otro')
    ], string='Tipo Horario')
    consider_holidays = fields.Boolean(string='Tener en Cuenta Festivos')

class resource_calendar_attendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    daytime_hours = fields.Float(string='Horas Diurnas',compute='_get_jornada_hours',store=True)
    night_hours = fields.Float(string='Horas Nocturnas',compute='_get_jornada_hours',store=True)

    @api.depends('hour_from','hour_to')
    def _get_jornada_hours(self):
        for record in self:
            hour_from = record.hour_from if record.hour_from else 0
            hour_to = record.hour_to if record.hour_to else 0
            #Calcular horas diurnas y nocturnas
            daytime_hours_initial = float(self.env['ir.config_parameter'].sudo().get_param('zue_planning.daytime_hours_initial')) or False
            daytime_hours_finally = float(self.env['ir.config_parameter'].sudo().get_param('zue_planning.daytime_hours_finally')) or False
            night_hours_initial = float(self.env['ir.config_parameter'].sudo().get_param('zue_planning.night_hours_initial')) or False
            night_hours_finally = float(self.env['ir.config_parameter'].sudo().get_param('zue_planning.night_hours_finally')) or False
            if daytime_hours_initial and daytime_hours_finally and night_hours_initial and night_hours_finally:
                if hour_from >= daytime_hours_initial and hour_to <= daytime_hours_finally:
                    record.night_hours = 0
                    record.daytime_hours = hour_to - hour_from + 24 if hour_to < hour_from else hour_to - hour_from
                elif (hour_from >= night_hours_initial and hour_to <= 24) or (hour_from >= 0 and hour_to <= night_hours_finally):
                    record.night_hours = hour_to - hour_from + 24 if hour_to < hour_from else hour_to - hour_from
                    record.daytime_hours = 0
                elif hour_from >= daytime_hours_initial and hour_from <= daytime_hours_finally and hour_to >= daytime_hours_finally:
                    record.night_hours = hour_to - daytime_hours_finally + 24 if hour_to < daytime_hours_finally else hour_to - daytime_hours_finally
                    record.daytime_hours = daytime_hours_finally - hour_from + 24 if daytime_hours_finally < hour_from else daytime_hours_finally - hour_from
                elif (hour_from <= daytime_hours_initial and hour_to >= daytime_hours_finally and hour_to <= daytime_hours_finally)\
                        or (hour_from <= daytime_hours_initial and hour_to >= daytime_hours_initial and hour_to <= daytime_hours_finally):
                    record.night_hours = daytime_hours_initial - hour_from + 24 if daytime_hours_initial < hour_from else daytime_hours_initial - hour_from
                    record.daytime_hours = hour_to - daytime_hours_initial + 24 if hour_to < daytime_hours_initial else hour_to - daytime_hours_initial
                elif hour_from <= daytime_hours_initial and hour_to >= daytime_hours_finally:
                    record.night_hours = daytime_hours_initial - hour_from + 24 if daytime_hours_initial < hour_from else daytime_hours_initial - hour_from
                    record.daytime_hours = daytime_hours_finally - daytime_hours_initial + 24 if daytime_hours_finally < daytime_hours_initial else daytime_hours_finally - daytime_hours_initial
                    record.night_hours += hour_to - daytime_hours_finally + 24 if hour_to < daytime_hours_finally else hour_to - daytime_hours_finally
                else:
                    record.night_hours = 0
                    record.daytime_hours = 0
            else:
                record.night_hours = 0
                record.daytime_hours = 0

