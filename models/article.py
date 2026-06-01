from odoo import models, fields

class ARFBArticle(models.Model):
    _name = "ar.fb.article"
    _description = "Article fourniture bureau"
    _rec_name = "description"
    _order = "id desc"

    description = fields.Char(string="Description", required=True)

    disponible = fields.Boolean(string="Disponible", default=True)