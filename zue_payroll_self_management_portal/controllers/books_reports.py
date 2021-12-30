#-*- coding: utf-8 -*-
import io
import re

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from PyPDF2 import  PdfFileReader, PdfFileWriter

from odoo.http import request, route, Controller
from odoo.tools.safe_eval import safe_eval


class ZuePayrollBooksReportsPortal(Controller):
    @route(["/zue_payroll_self_management_portal/book_vacation"], type='http', auth='user')
    def get_book_vacation(self, **post):
        if not request.env.user:
            return request.not_found()

        obj_employee = request.env['hr.employee.public'].search([('user_id','=',request.env.user.id)], limit=1)
        obj_contract = request.env['hr.contract.public'].search([('employee_id','=',obj_employee.id),('state','=','open')], limit=1)                           

        pdf_writer = PdfFileWriter()

        for contract in obj_contract:
            report = request.env.ref('zue_payroll_self_management_portal.report_book_vacation_portal_action', False)
            pdf_content, _ = report.render_qweb_pdf(contract.id)
            reader = PdfFileReader(io.BytesIO(pdf_content), strict=False, overwriteWarnings=False)

            for page in range(reader.getNumPages()):
                pdf_writer.addPage(reader.getPage(page))

        _buffer = io.BytesIO()
        pdf_writer.write(_buffer)
        merged_pdf = _buffer.getvalue()
        _buffer.close()
        
        report_name = "Libro de vacaciones"

        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(merged_pdf)),
            ('Content-Disposition', 'attachment; filename=' + report_name + '.pdf;')
        ]

        return request.make_response(merged_pdf, headers=pdfhttpheaders)

    @route(["/zue_payroll_self_management_portal/book_cesantias"], type='http', auth='user')
    def get_book_cesantias(self, **post):
        if not request.env.user:
            return request.not_found()

        obj_employee = request.env['hr.employee.public'].search([('user_id','=',request.env.user.id)], limit=1)
        obj_contract = request.env['hr.contract.public'].search([('employee_id','=',obj_employee.id),('state','=','open')], limit=1)                           

        pdf_writer = PdfFileWriter()

        for contract in obj_contract:
            report = request.env.ref('zue_payroll_self_management_portal.report_book_cesantias_portal_action', False)
            pdf_content, _ = report.render_qweb_pdf(contract.id)
            reader = PdfFileReader(io.BytesIO(pdf_content), strict=False, overwriteWarnings=False)

            for page in range(reader.getNumPages()):
                pdf_writer.addPage(reader.getPage(page))

        _buffer = io.BytesIO()
        pdf_writer.write(_buffer)
        merged_pdf = _buffer.getvalue()
        _buffer.close()
        
        report_name = "Libro de cesantías"

        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(merged_pdf)),
            ('Content-Disposition', 'attachment; filename=' + report_name + '.pdf;')
        ]

        return request.make_response(merged_pdf, headers=pdfhttpheaders)
