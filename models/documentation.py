from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ARFBDocumentation(models.Model):
    _name = "ar.fb.documentation"
    _description = "FB - Documentation"
    _order = "create_date desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    description = fields.Char(string="Description", required=True, tracking=True)

    file_data = fields.Binary(string="Fichier", required=False, attachment=True, tracking=True)
    file_name = fields.Char(string="Nom du fichier", required=False, tracking=True)

    link_url = fields.Char(string="Lien", tracking=True)

    created_by = fields.Many2one(
        "res.users",
        string="Réalisé par",
        related="create_uid",
        store=True,
        readonly=True,
    )
    created_on = fields.Datetime(string="Date", related="create_date", store=True, readonly=True)

    @api.constrains("file_data", "link_url")
    def _check_file_or_link(self):
        for rec in self:
            if not rec.file_data and not rec.link_url:
                raise ValidationError(_("Vous devez renseigner soit un fichier, soit un lien."))