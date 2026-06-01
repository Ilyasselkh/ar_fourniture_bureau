from odoo import models, fields

class ARFBTraiteur(models.Model):
    _name = "ar.fb.traiteur"
    _description = "Personnes qui traitent"
    _rec_name = "employee_id"
    _order = "id desc"

    employee_id = fields.Many2one("hr.employee", string="Employé", required=True)

    disponible = fields.Boolean(string="Disponible", default=True)