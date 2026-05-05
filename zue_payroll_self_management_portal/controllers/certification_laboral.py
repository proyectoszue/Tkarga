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
        obj_portal_design = request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', request.env.user.company_id.id)], limit=1)
        obj_version = request.env['hr.version.public'].search(
            [('employee_id', '=', obj_employee.id), ('contract_date_end', '=', False)], limit=1)
        version = obj_version.name if obj_version else ''
        generation_date = datetime.today()
        generation_date = generation_date.strftime('%d-%m-%Y')
        report_name = "Certificado Laboral"

        return request.render('zue_payroll_self_management_portal.labor_certification',{'version':version,'report_name':report_name,'generation_date':generation_date, 'portal_design':obj_portal_design})

    @route(["/zue_payroll_self_management_portal/certification_print"], type='http', auth='user', website=True, csrf=False)
    def get_certification_print(self, **post):
        if not request.env.user:
            return request.not_found()

        obj_employee = request.env['hr.employee.public'].search([('user_id','=',request.env.user.id)], limit=1)
        obj_version = request.env['hr.version.public'].search([('employee_id','=',obj_employee.id),('contract_date_end','=',False)], limit=1)

        history = {
            'version_id' : obj_version.id,
            'date_generation' : datetime.today().date(),
            'info_to' : post['addressed']
        }

        obj_history = request.env['hr.labor.certificate.history'].create(history)

        pdf_writer = PdfFileWriter()

        # report = request.env.ref('zue_payroll_self_management_portal.report_certificacion_laboral_portal_action', False)
        pdf_content, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf('zue_payroll_self_management_portal.report_certificacion_laboral_portal_action', [obj_history.id])
        # reader = PdfFileReader(io.BytesIO(pdf_content), strict=False)

        # for page in range(reader.getNumPages()):
        #     pdf_writer.addPage(reader.getPage(page))

        values_certification = {
            'pdf_name': f"Certificado - {obj_history.version_id.name if obj_history.version_id else ''} - {obj_history.sequence or ''}"
        }

        request.env['hr.labor.certificate.history'].sudo().search([('id', '=', obj_history.id)], limit=1).write(values_certification)
        # _buffer = io.BytesIO()
        # pdf_writer.write(_buffer)
        # merged_pdf = _buffer.getvalue()
        # _buffer.close()
        
        report_name = "Certificado Laboral"

        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_content)),
            ('Content-Disposition', 'attachment; filename=' + report_name + '.pdf;')
        ]

        return request.make_response(pdf_content, headers=pdfhttpheaders)

