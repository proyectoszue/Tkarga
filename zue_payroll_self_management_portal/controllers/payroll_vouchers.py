#-*- coding: utf-8 -*-
import io
import re

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from PyPDF2 import  PdfFileReader, PdfFileWriter

from odoo.http import request, route, Controller
from odoo.tools.safe_eval import safe_eval


class ZuePayrollVouchersPortal(Controller):
    @route('/zue_payroll_self_management_portal/generate_vouchers', auth='user', website=True)
    def generate_vouchers(self, **kw):
        if not request.env.user:
            return request.not_found()
            
        obj_employee = request.env['hr.employee.public'].search([('user_id','=',request.env.user.id)], limit=1)
        company = obj_employee.company_id.name

        #Filtros de años (Se traen los ultimos 3 años)
        years = []
        year = datetime.today().year
        year_min = year-2
        while year > year_min:            
            year_dict = {'id':year,
                            'text': year
                            }
            years.append(year_dict)
            year = year - 1

        return request.render('zue_payroll_self_management_portal.generate_vouchers',{'company':company,'years':years})

    @route(["/zue_payroll_self_management_portal/payslip"], type='http', auth='user', website=True, csrf=False)
    def get_payroll_report_print(self, **post):
        if not request.env.user:
            return request.not_found()
        
        month = int(post['month'])
        year = int(post['year'])

        #Obtener rango de fechas
        date_start = '01/'+str(month)+'/'+str(year)
        date_start = datetime.strptime(date_start, '%d/%m/%Y')      

        date_end = date_start + relativedelta(months=1)
        date_end = date_end - timedelta(days=1)
        
        date_start = date_start.date()
        date_end = date_end.date()

        #Obtener nóminas
        report_name = 'Nómina'

        obj_employee = request.env['hr.employee.public'].search([('user_id','=',request.env.user.id)], limit=1)
        payslips = request.env['hr.payslip.public'].search([('state','=','done'),('employee_id','=',obj_employee.id),('date_from','>=',date_start),('date_to','<=',date_end)])
        
        pdf_writer = PdfFileWriter()

        for payslip in payslips:
            report_name = payslip.struct_id.name + ' del ' + str(year) + '-' +  str(month)
            report = request.env.ref('zue_payroll_self_management_portal.report_payslip_portal_action', False)
            pdf_content, _ = report.render_qweb_pdf(payslip.id)
            reader = PdfFileReader(io.BytesIO(pdf_content), strict=False, overwriteWarnings=False)

            for page in range(reader.getNumPages()):
                pdf_writer.addPage(reader.getPage(page))

        _buffer = io.BytesIO()
        pdf_writer.write(_buffer)
        merged_pdf = _buffer.getvalue()
        _buffer.close()

        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(merged_pdf)),
            ('Content-Disposition', 'attachment; filename=' + report_name + '.pdf;')
        ]

        return request.make_response(merged_pdf, headers=pdfhttpheaders)      
    

