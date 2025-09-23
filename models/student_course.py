from odoo import models,fields,api

class StudentClassName(models.Model):
    _name = 'student.class.name'
    _description = 'Available Courses and its fees'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    course_no = fields.Integer(string='Course ID')
    name = fields.Char(string='Class Name', required=True)
    duration = fields.Integer('Course Duration')
    admission_fee = fields.Float('Admission Fee')
    term_one_fee = fields.Float(string='Term -1 Fee', )
    term_two_fee = fields.Float(string='Term -2 Fee', )
    term_three_fee = fields.Float(string='Term -3 Fee', )
    max_count = fields.Integer(string='Available Seat')
    is_locked = fields.Boolean(string='Locked', default=False)
    active = fields.Boolean(string='Active', default=True)
    company_logo = fields.Binary(string='Company Logo', related='company_id.logo', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)

    student_ids = fields.One2many('student.master', 'course_id', string="Students")
    year_line_ids = fields.One2many('course.year.line', 'course_id', string="Years")
    batch_ids = fields.One2many('student.division', 'course_id', string="Batches")


    def _generate_year_lines(self):
        """Helper to regenerate year lines according to duration"""
        for rec in self:
            if rec.duration and rec.duration > 0:
                rec.year_line_ids.unlink()  # clear old lines
                lines = []
                for i in range(1, rec.duration + 1):
                    year_name = f"{i}{'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th' } Year"
                    lines.append((0, 0, {
                        'name': year_name,
                        'sequence': i,
                    }))
                rec.year_line_ids = lines

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record, vals in zip(records, vals_list):
            if vals.get("duration"):
                record._generate_year_lines()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "duration" in vals:
            self._generate_year_lines()
        return res

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string="Status", default='draft', tracking=True)

    def action_save(self):
        self.write({'is_locked': True})
        for rec in self:
            rec.state = 'confirmed'
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_edit(self):
        self.write({'is_locked': False})
        for rec in self:
            rec.state = 'draft'
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def action_back(self):
        # Do nothing if the record is new (no ID)
        if not self.id:
            return {'type': 'ir.actions.do_nothing'}
        action = self.env.ref("school_master_pro.student_course_action_window").read()[0]
        return {
            "type": "ir.actions.client",
            "tag": "do-action-replace-history",
            "params": {"action": action},
        }

    @api.depends('max_count')
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = self.env['student.master'].search_count([
                ('student_class_name', '=', rec.id),
                ('active', '=', True)
            ])




class CourseYearLine(models.Model):
    _name = 'course.year.line'
    _description = 'Course Year Line'
    _order = 'sequence asc'

    name = fields.Char(string="Year Name", required=True)
    sequence = fields.Integer(string="Year No.", required=True)
    course_id = fields.Many2one(
        'student.class.name',
        string="Course",
        required=True,
        ondelete="cascade"
    )

    active = fields.Boolean(string="Active", default=True)
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)


    @api.depends('course_id', 'name')
    def _compute_display_name(self):
        for rec in self:
            course = rec.course_id.name if rec.course_id else ''
            year = rec.name or ''
            rec.display_name = (f"{course} - {year}").strip(' -')

    def name_get(self):
        """Ensure every widget that uses name_get shows course - year"""
        return [(rec.id, rec.display_name or '') for rec in self]