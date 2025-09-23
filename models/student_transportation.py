from odoo import models, fields, api


class StudentTransportation(models.Model):
    _name = 'student.transportation'
    _description = 'Student Transportation Details'
    _rec_name = 'student_id'

    student_id = fields.Many2one('student.master', string='Student Name')
    basic_fee = fields.Float('Basic Transport Fee')
    student_trans = fields.Selection([('school_bus', 'School Bus'), ('auto', 'Auto'), ('self', 'Self')],
                                     string='Transportation', required=True)
    transport_mode = fields.Selection([('one_way', 'One Way'), ('two_way', 'Two Way')], string='Transportation Mode',
                                      required=True)

    transportation_fee = fields.Float(string='Monthly Fee',compute='_compute_monthly_fee',store=True)
    is_locked = fields.Boolean(string='Locked', default=False)

    def action_save(self):
        self.write({'is_locked': True})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_edit(self):
        self.write({'is_locked': False})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.depends('transport_mode', 'student_trans','basic_fee')
    def _compute_monthly_fee(self):
        for record in self:
            if record.student_trans == 'school_bus':
                if record.transport_mode == 'two_way':
                    record.transportation_fee = record.basic_fee
                elif record.transport_mode == 'one_way':
                    record.transportation_fee = record.basic_fee/2
                else:
                    record.transportation_fee = 0
            else:
                record.transportation_fee = 0

    # name = fields.Char(string='Teacher Name', required=True)
    # gender= fields.Selection([('male','Male'),('female','Female')],string='Gender',default='male')
    # doj= fields.Date('Date of Joining')
    # transportation_fee = fields.Char(string='Servicing Years',compute='_compute_year_of_service',
    #     store=True  # Optional: only include if you want to store the computed value
    # )
    #
    #
    # contact_no = fields.Char(string='Contact No')
    # emergency_contact = fields.Char(string='Emergency Contact')
    # address = fields.Text('Address')
    # designation_id = fields.Many2one('teacher.designation',string='Designation')
    # std = fields.Many2many('student.class.no',string='Class')
    #
    # # display_std = fields.Char(string="Std Display", compute="_compute_display_std")
    #
    # # def _compute_display_std(self):
    # #     for record in self:
    # #         record.display_std = ", ".join(record.std.mapped('name')) if record.std else ""
    #
    # @api.depends('doj')
    # def _compute_year_of_service(self):
    #     today = date.today()
    #     for record in self:
    #         if record.doj:
    #             delta = relativedelta(today, record.doj)
    #             record.year_of_service = f"{delta.years}y {delta.months}m {delta.days}d"
    #         else:
    #             record.year_of_service = "0y 0m 0d"
