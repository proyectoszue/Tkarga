from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class zue_tracking_activities(models.Model):
    _name = 'zue.tracking.activities'
    _description = 'Seguimiento de actividades'
    _auto = False

    z_activity = fields.Html(string='Contenido Actividad')
    z_activity_type_id = fields.Many2one('mail.activity.type',string='Tipo de actividad')
    z_create_uid = fields.Many2one('res.users',string='Creado por')
    z_create_date = fields.Datetime(string='Fecha creación', help='Esta fecha se pierde una vez sea realizada la actividad')
    z_user_id = fields.Many2one('res.users',string='Asignado a')
    z_date_deadline = fields.Datetime(string='Fecha vencimiento', help='Esta fecha se pierde una vez sea realizada la actividad')
    z_date_done = fields.Datetime(string='Fecha de realizado')
    z_state = fields.Char(string='Estado')

    @api.model
    def _query(self):
        return f'''
        Select Row_Number() Over(Order By z_state,z_create_date,z_user_id) as id, * 
        From (
            Select a.summary || ' <br> ' || a.note as z_activity, a.activity_type_id as z_activity_type_id,
                a.create_uid as z_create_uid, a.create_date as z_create_date,a.user_id as z_user_id, 
                a.date_deadline as z_date_deadline, '1900-01-01' as z_date_done,'POR HACER' as z_state
            From mail_activity as a
            Union
            Select 
                a.body as activity, a.mail_activity_type_id,b.id as create_uid, '1900-01-01' as create_date,a.create_uid, '1900-01-01' as date_deadline, a.create_date as date_done,
                'REALIZADO' as state
            From mail_message as a 
            Inner join res_users as b on a.author_id = b.partner_id
            Where mail_activity_type_id is not null
        ) as A
        '''

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
                %s
            )
        ''' % (
            self._table, self._query()
        ))