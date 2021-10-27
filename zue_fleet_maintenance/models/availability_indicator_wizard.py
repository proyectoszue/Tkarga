# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) BIG OutSourcing (<http://bigoutsourcing.com.co>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: Oscar Javier Velasco ovelasco@bigoutsourcing.com.co
#    Planified by: Juan Carlos Barrero Mejia
#    Finance by: BIG OUTSOURCING LTDA. http://www.bigoutsourcing.com.co
#    Audited by: Juan Carlos Barrero Mejia jbarrero@bigoutsourcing.com.co
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

from odoo import models, fields, api, _
from datetime import datetime, timedelta
import calendar
from calendar import monthrange
from odoo.exceptions import ValidationError, UserError

class availability_indicator_wizard(models.TransientModel):
    _name = 'availability.indicator.wizard'
    _description = "Informe de Disponibilidad"

    start_date = fields.Date(string='Fecha de Inicio', required=True)
    end_date = fields.Date(string='Fecha Final', required=True)
    hours_24 = fields.Boolean('24 Horas')
    start_hour = fields.Integer('Hora de Inicio (24H)')
    end_hour = fields.Integer('Hora Final (24H)')
    all_services = fields.Boolean('Todos los Servicios')
    service_ids = fields.Many2many('mntc.services.type', string='Tipo(s) de Servicio')
    company_id = fields.Many2one('res.company', string='Company') # compute='get_company'

    @api.model
    def _get_default_id(self):
        return self.env.ref('big_documents_type.mntc_documents_types_availability_indicator')

     
    def get_company(self):
        self.company_id = self.env.user.company_id
        return True

     
    def print_availability_report(self):
        
       # start_date = datetime.strptime(self.start_date, '%Y-%m-%d')
       #  end_date = datetime.strptime(self.end_date, '%Y-%m-%d')
       
        if self.start_date > datetime.now().date() or self.end_date > datetime.now().date():
            raise ValidationError(_("Las fechas seleccionadas son mayores que la fecha actual.")) 

        datas = {
             'id': self.id,
             'model': 'availability.indicator.wizard'             
            }

        return {
                   'type': 'ir.actions.report',
                   'report_name': 'zue_fleet_maintenance.availability_indicator_report_document',
                   'report_type': 'qweb-pdf',
                   'datas': datas,
                   #'context': self._context
               }
     
    def get_days_month(self):
        
        start, end = self.transform_date()

        days = {}
        for year_number in range(start.year, end.year+1):
            if start.year != end.year:
                if year_number == start.year:
                    start_month = start.month
                    end_month = 12
                elif year_number == end.year:
                    start_month = 1
                    end_month = end.month
            else:
                start_month = start.month
                end_month = end.month
            for month_number in range(start_month, end_month + 1):
                first_monday, qty_days = monthrange(year_number, month_number)
                days[month_number] = [x for x in range(1, qty_days+1)]

        return days

     
    def get_month_name(self):

        start, end = self.transform_date()
        months = []
        for year_number in range(start.year, end.year+1):
            if start.year != end.year:
                if year_number == start.year:
                    start_month = start.month
                    end_month = 12
                elif year_number == end.year:
                    start_month = 1
                    end_month = end.month
            else:
                start_month = start.month
                end_month = end.month
            for month_number in range(start_month, end_month + 1):
                month_name = calendar.month_name[month_number] + " " + str(year_number)
                months.append((month_name.upper(), month_number, year_number))

        return months

     
    def transform_date(self):
        if self.hours_24:
            start_date = str(self.start_date) + ' 00:00:00'
            end_date = str(self.end_date) + ' 23:59:59'
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        else:
            start_date = str(self.start_date) + ' ' + str(self.start_hour) + ':00:00'
            end_date = str(self.end_date) + ' ' +str(self.end_hour) + ':00:00'
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
        
        return start_datetime, end_datetime

     
    def get_services_data(self):

        if self.all_services:
            service_ids = [x for x in self.env['mntc.services.type'].search([('id', '>', '0')])]
        else:
            service_ids = [x for x in self.service_ids]
        
        services_data = {}
        for service_id in service_ids:
            services_data[service_id.id] = [service_id.name, service_id.margin]
            qty_vehicles = 0
            count_vehicles = [str(qty_vehicles)]
            for vehicle in self.env['fleet.vehicle'].search([('service_type_id', '=', service_id.id)]):
                qty_vehicles += 1
                if qty_vehicles <= 10: 
                    count_vehicles.append(str(qty_vehicles))

            max_vehicle = str(count_vehicles[-1]) + "+"
            count_vehicles.append(max_vehicle)

            count_vehicles = count_vehicles[::-1]
            services_data[service_id.id].append(count_vehicles)
        print("------------------> DATA", services_data)
        return services_data

     
    def get_quantity_per_day(self, day, month, year, service):
        
        if self.hours_24:
            start_date = '%04d' % year + "-" + '%02d' % month + "-" + '%02d' % day + ' 00:00:00'
            end_date = '%04d' % year + "-" + '%02d' % month + "-" + '%02d' % day + ' 23:59:59'
        else:
            start_date = '%04d' % year + "-" + '%02d' % month + "-" + '%02d' % day + " " + str(self.start_hour) + ":00:00"
            end_date = '%04d' % year + "-" + '%02d' % month + "-" + '%02d' % day + " " + str(self.end_hour) + ":59:59"

        count = 0
        self_end_date = datetime.strptime(str(self.end_date), '%Y-%m-%d') + timedelta(days=1)
        if start_date >= str(self.start_date) and end_date <= str(self_end_date):
            vehicles_counted = []
            for io in self.env['mntc.io'].search([('incoming_date', '<=', end_date), '|', ('outgoing_date', '>=', start_date), ('outgoing_date', '=', False)]):
                if io.vehicle_id.id not in vehicles_counted and io.vehicle_id.service_type_id.id == service:
                    if datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S') <= datetime.now():
                        count += 1
                        vehicles_counted.append(io.vehicle_id.id)
        return count
    
     
    def get_max_per_day(self, service):
        
        max_per_day = 0
        start, end = self.transform_date() 
        for year_number in range(start.year, end.year+1):
            if start.year != end.year:
                if year_number == start.year:
                    start_month = start.month
                    end_month = 12
                elif year_number == end.year:
                    start_month = 1
                    end_month = end.month
            else:
                start_month = start.month
                end_month = end.month
            for month_number in range(start_month, end_month + 1):
                print("--------------> MONTH NUMBER", month_number)
                if start_month == end_month:
                    for day in range(start.day, end.day+1):
                        day_qty = self.get_quantity_per_day(day, start.month, start.year, service)
                        if day_qty > max_per_day:
                            max_per_day = day_qty
                else:
                    first_monday, qty_days = monthrange(year_number, month_number)
                    for day in range(1, qty_days+1):
                        day_qty = self.get_quantity_per_day(day, start.month, start.year, service)
                        if day_qty > max_per_day:
                            max_per_day = day_qty
            
        if max_per_day > 0:
            count = [i for i in range(1, max_per_day+1)]
        else:
            count = []
        return count
    
     
    def get_movile_day(self, day, month, year, service):
        
        vehicles_ids = []
        moviles = []
        if self.hours_24:
            start_date = '%04d' % year + "-" + '%02d' % month + "-" + '%02d' % day + " 00:00:00"
            end_date = '%04d' % year + "-" + '%02d' % month + "-" + '%02d' % day + " 23:59:59"
        else:
            start_date = '%04d' % year + "-" + '%02d' % month + "-" + '%02d' % day + " " + str(self.start_hour) + ":00:00"
            end_date = '%04d' % year + "-" + '%02d' % month + "-" + '%02d' % day + " " + str(self.end_hour) + ":59:59"

        self_end_date = datetime.strptime(str(self.end_date), '%Y-%m-%d') + timedelta(days=1)
        if start_date >= str(self.start_date) and end_date <= str(self_end_date):

            for io in self.env['mntc.io'].search([('incoming_date', '<=', end_date), '|', ('outgoing_date', '>=', start_date), ('outgoing_date', '=', False)]):
                if io.vehicle_id.service_type_id.id == service:
                    if datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S') <= datetime.now():
                        vehicles_ids.append(io.vehicle_id.id)

            vehicles_ids.sort()
            vehicles_counted = []
            for vehicle in self.env['fleet.vehicle'].browse(vehicles_ids):
                if vehicle.id not in vehicles_counted:
                    vehicles_counted.append(vehicle.id)
                    moviles.append(vehicle.movil_nro)
        # print"-----------------------> MOVILES", moviles
        return moviles
