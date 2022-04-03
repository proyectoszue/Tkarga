#-*- coding: utf-8 -*-
import io
import re

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from PyPDF2 import  PdfFileReader, PdfFileWriter

from odoo.http import request, route, Controller
from odoo.tools.safe_eval import safe_eval


class ZuePayrollCertificationLaboralPortal(Controller):
    @route(["/zue_payroll_self_management_portal/labor_certification"], auth='user', website=True)
    def get_certification(self, **kw):
        if not request.env.user:
            return request.not_found()

        obj_employee = request.env['hr.employee.public'].search([('user_id','=',request.env.user.id)], limit=1)
        contract = obj_employee.contract_id.name
        generation_date = datetime.today()
        generation_date = generation_date.strftime('%d-%m-%Y')
        report_name = "Certificado Laboral"

        return request.render('zue_payroll_self_management_portal.labor_certification',{'contract':contract,'report_name':report_name,'generation_date':generation_date})

    @route(["/zue_payroll_self_management_portal/certification_print"], type='http', auth='user', website=True, csrf=False)
    def get_certification_print(self, **post):
        if not request.env.user:
            return request.not_found()

        obj_employee = request.env['hr.employee.public'].search([('user_id','=',request.env.user.id)], limit=1)
        obj_contract = request.env['hr.contract.public'].search([('employee_id','=',obj_employee.id),('state','=','open')], limit=1)

        history = {
            'contract_id' : obj_contract.id,
            'date_generation' : datetime.today().date(),
            'info_to' : post['addressed']
        }

        obj_history = request.env['hr.labor.certificate.history'].create(history)

        pdf_writer = PdfFileWriter()

        report = request.env.ref('zue_payroll_self_management_portal.report_certificacion_laboral_portal_action', False)
        pdf_content, _ = report.render_qweb_pdf(obj_history.id)
        reader = PdfFileReader(io.BytesIO(pdf_content), strict=False, overwriteWarnings=False)

        for page in range(reader.getNumPages()):
            pdf_writer.addPage(reader.getPage(page))

        values_certification = {
            'pdf_name' : 'Certificado - ' + obj_history.contract_id.name + ' - ' + obj_history.sequence
        } 

        obj_history = request.env['hr.labor.certificate.history'].search([('id', '=', obj_history.id)], limit=1).write(values_certification)
        _buffer = io.BytesIO()
        pdf_writer.write(_buffer)
        merged_pdf = _buffer.getvalue()
        _buffer.close()
        
        report_name = "Certificado Laboral"

        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(merged_pdf)),
            ('Content-Disposition', 'attachment; filename=' + report_name + '.pdf;')
        ]

        return request.make_response(merged_pdf, headers=pdfhttpheaders)

