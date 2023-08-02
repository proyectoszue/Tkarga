import io
import re

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo.http import request, route, Controller

class ZuePayrollDocumentsEmployeePortal(Controller):

    @route('/zue_payroll_self_management_portal/documents', auth='user', website=True)
    def documents_data(self, **kw):
        if not request.env.user:
            return request.not_found()

        obj_portal_design = request.env['zue.hr.employee.portal.design'].search(
            [('z_company_design_id', '=', request.env.user.company_id.id)], limit=1)
        obj_employee = request.env['hr.employee.public'].search([('user_id', '=', request.env.user.id)], limit=1)
        if len(obj_employee) > 0:
            for employee in obj_employee:
                documents = employee.get_info_documents_portal(user_id=request.env.user.id,cant_expirados=0)

                return request.render('zue_payroll_self_management_portal.documents_data',{'documents': documents, 'portal_design':obj_portal_design})