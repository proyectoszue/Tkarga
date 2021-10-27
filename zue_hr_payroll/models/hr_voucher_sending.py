# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import odoo
import base64
import threading
#---------------------------Modelo para generar Archivo plano de pago de nómina-------------------------------#

class hr_voucher_sending_failed(models.Model):
    _name = 'hr.voucher.sending.failed'
    _description = 'Ejecución comprobantes de nómina Fallidos'
    
    voucher_id = fields.Many2one('hr.voucher.sending', 'Ejecución comprobantes')
    payslip_id = fields.Many2one('hr.payslip',string='Nómina')    
    employee_id = fields.Many2one(related='payslip_id.employee_id', string='Empleado')

class hr_voucher_sending(models.Model):
    _name = 'hr.voucher.sending'
    _description = 'Ejecución comprobantes de nómina'

    send_type = fields.Selection([('send', 'Enviar por correo electrónico')], string='Proceso', default='send',required=True)
    generation_type = fields.Selection([('lote', 'Por lote'),
                                        ('individual', 'Por Empleado')], string='Tipo', default='lote', required=True)
    #Campo Lote
    payslip_run_id = fields.Many2one('hr.payslip.run',string='Lote de nómina')    
    #Campos Empleados
    employee_id = fields.Many2one('hr.employee',string='Empleado')    
    payslip_id = fields.Many2one('hr.payslip',string='Nómina', domain="[('employee_id','=',[employee_id])]")
        
    #Inf Adicional Correo
    subject = fields.Char(string='Asunto')    
    description = fields.Text(string='Cuerpo del correo') 

    #Envios fallidos
    vouchers_failed_ids = fields.One2many('hr.voucher.sending.failed', 'voucher_id','Envíos fallidos')

    def name_get(self):
        result = []
        for record in self: 
            if record.payslip_run_id:
                result.append((record.id, "Comprobantes de nómina - ".format(record.payslip_run_id.name)))
            else:
                result.append((record.id, "Comprobantes de nómina - ".format(record.payslip_id.name)))
        return result

    def create_document_inmemory(self,records):
        with odoo.api.Environment.manage():
            registry = odoo.registry(self._cr.dbname)
            with registry.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})                
                for payslip in records:
                    obj_payslip = env['hr.payslip'].search([('id', '=', payslip)])
                    report = obj_payslip.struct_id.report_id
                    pdf_content, content_type = report.render_qweb_pdf(obj_payslip.id)
                    pdf_name = obj_payslip.struct_id.name +' - '+obj_payslip.employee_id.name+' - '+str(obj_payslip.date_to) + '.pdf'
                    
                    try:
                        email_vals = {}
                        identificacion  = obj_payslip.employee_id.identification_id
                        nombre_empleado = obj_payslip.employee_id.name
                        correo_envio    = obj_payslip.employee_id.work_email
                        # body message
                        message = "Estimado "+ nombre_empleado + "<br/><br/>"
                        message += "Adjunto encontrara la informacion de la ultima liquidacion y pago de su nomina<br/><br/><br/>"
                        message += "por favor no responda este correo, esto es un mensaje automatico."
                        pdf_content = base64.b64encode(pdf_content)

                        data_attach = {'name':"Comprobante_nomina_"+identificacion+"_"+obj_payslip.name+".pdf", 'type':'binary', 'datas':pdf_content,'res_name':pdf_name,'store_fname':pdf_name,'res_model':'hr.payslip','res_id':obj_payslip.id}
                        atts_id = env['ir.attachment'].create(data_attach)
                        if atts_id:
                            email_vals.update({'subject':self.subject,
                                                'email_to': correo_envio,
                                                'email_from': self.env.user.email, 
                                                'body_html':message.encode('utf-8'),
                                                'attachment_ids': [(6, 0, [atts_id.id])] })
                            # create and send email
                            if email_vals:
                                email_id = env['mail.mail'].create(email_vals)
                                if email_id:
                                    email_id.send()                    
                    except Exception as error:
                        values = {
                            'voucher_id': self.id,
                            'payslip_id': obj_payslip.id
                        }
                        env['hr.voucher.sending.failed'].create(values)

    def generate_voucher(self):
        self.env['hr.voucher.sending.failed'].search([('voucher_id', '=', self.id)]).unlink()
        date_start_process = datetime.now()
        date_finally_process = datetime.now()
        array_thread = []
        if self.generation_type == 'lote':
            obj_payslip = self.env['hr.payslip'].search([('payslip_run_id', '=', self.payslip_run_id.id)])
            #Guardar las liquidaciones en un arreglo en lotes de 50
            payslips_array, i, j = [], 0 , 50            
            while i <= len(obj_payslip):                
                payslips_array.append(obj_payslip[i:j].ids)
                i = j
                j += 50            
            #Enviar comprobantes en los lotes ejecutados
            i = 1
            for send in payslips_array:
                #msg = 'Enviando Comprobantes | Parte '+str(i)+' de '+str(len(payslips_array))+' | Total de comprobantes: '+str(len(obj_payslip))
                t = threading.Thread(target=self.create_document_inmemory, args=(send,))                
                t.start()
                array_thread.append(t)
                i += 1        
        else:
            send = [self.payslip_id.id]
            t = threading.Thread(target=self.create_document_inmemory, args=(send,))
            t.start()  
            array_thread.append(t)

        for hilo in array_thread:
                while hilo.is_alive():
                    date_finally_process = datetime.now() 

        time_process = date_finally_process - date_start_process
        time_process = time_process.seconds / 60
        print(time_process) 

    def generate_voucher_failed(self):
        obj_payslip = self.env['hr.payslip'].search([('id', 'in', self.vouchers_failed_ids.payslip_id.ids)])
        date_start_process = datetime.now()
        date_finally_process = datetime.now()
        array_thread = []
        payslips_array, i, j = [], 0 , 50            
        while i <= len(obj_payslip):                
            payslips_array.append(obj_payslip[i:j].ids)
            i = j
            j += 50     

        self.env['hr.voucher.sending.failed'].search([('voucher_id', '=', self.id)]).unlink()
        #Enviar comprobantes en los lotes ejecutados
        i = 1
        for send in payslips_array:
            #msg = 'Enviando Comprobantes | Parte '+str(i)+' de '+str(len(payslips_array))+' | Total de comprobantes: '+str(len(obj_payslip))
            t = threading.Thread(target=self.create_document_inmemory, args=(send,))                
            t.start()
            array_thread.append(t)
            i += 1 

        for hilo in array_thread:
                while hilo.is_alive():
                    date_finally_process = datetime.now() 

        time_process = date_finally_process - date_start_process
        time_process = time_process.seconds / 60
        print(time_process)                 
        




    
    
