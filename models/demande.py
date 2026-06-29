from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
import base64
import gzip
import logging


_logger = logging.getLogger(__name__)


class ARFBDemande(models.Model):
    _name = "ar.fb.demande"
    _description = "Demande fourniture bureau"
    _order = "id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Référence", default="Nouveau", readonly=True, copy=False)

    state = fields.Selection(
        [
            ("new", "Nouvelle"),
            ("n1", "Validation N+1"),
            ("processing", "Traitement"),
            ("received", "Livrée"),
            ("refused", "Refusée"),
        ],
        string="Statut",
        default="new",
        tracking=True,
        required=True,
    )

    def _default_employee(self):
        return self.env["hr.employee"].search([("user_id", "=", self.env.user.id)], limit=1)

    demandeur_id = fields.Many2one(
        "hr.employee",
        string="Demandeur",
        default=_default_employee,
        readonly=True,
        tracking=True,
    )

    department_id = fields.Many2one(
        "hr.department",
        string="Département",
        related="demandeur_id.department_id",
        store=True,
        readonly=True,
        tracking=True,
    )

    manager_n1_id = fields.Many2one(
        "hr.employee",
        string="Manager N+1",
        related="demandeur_id.parent_id",
        store=True,
        readonly=True,
        tracking=True,
    )

    
    is_manager_n1 = fields.Boolean(string="Manager N+1 ?", compute="_compute_acl_flags", store=False)
    can_process = fields.Boolean(string="Peut traiter ?", compute="_compute_acl_flags", store=False)
    is_demandeur = fields.Boolean(string="Demandeur ?", compute="_compute_acl_flags", store=False)
    can_edit_request = fields.Boolean(string="Peut modifier ?", compute="_compute_acl_flags", store=False)
    can_submit_n1 = fields.Boolean(string="Peut soumettre ?", compute="_compute_acl_flags", store=False)
    can_approve_n1 = fields.Boolean(string="Peut valider N+1 ?", compute="_compute_acl_flags", store=False)
    can_refuse_request = fields.Boolean(string="Peut refuser ?", compute="_compute_acl_flags", store=False)
    can_mark_received = fields.Boolean(string="Peut receptionner ?", compute="_compute_acl_flags", store=False)

    @api.depends_context("uid")
    def _compute_acl_flags(self):
        for rec in self:
            is_demandeur = rec._is_demandeur()
            is_manager = rec._is_manager_n1()
            can_process = rec._is_traitement_user()

            rec.is_demandeur = is_demandeur
            rec.is_manager_n1 = is_manager
            rec.can_process = can_process
            rec.can_edit_request = rec.state == "new" and is_demandeur
            rec.can_submit_n1 = rec.state == "new" and is_demandeur
            rec.can_approve_n1 = rec.state == "n1" and is_manager
            rec.can_mark_received = rec.state == "processing" and can_process
            rec.can_refuse_request = (
                (rec.state == "n1" and is_manager)
                or (rec.state == "processing" and can_process)
            )

    def _is_demandeur(self):
        self.ensure_one()
        return bool(self.demandeur_id and self.demandeur_id.user_id.id == self.env.user.id)

    def _is_manager_n1(self):
        self.ensure_one()
        return bool(self.manager_n1_id and self.manager_n1_id.user_id.id == self.env.user.id)

    def _is_traitement_user(self):
        self.ensure_one()
        if not self.env.user.has_group("ar_fourniture_bureau.group_ar_fb_traitement"):
            return False
        return bool(self.env["ar.fb.traiteur"].sudo().search_count([
            ("employee_id.user_id", "=", self.env.user.id),
            ("disponible", "=", True),
        ]))

    def _check_is_demandeur(self):
        self.ensure_one()
        if not self._is_demandeur():
            raise AccessError(_("Seul le demandeur concerne peut modifier ou soumettre cette demande."))

    def _check_is_manager_n1(self):
        """Sécurité serveur: autorise seulement le manager N+1 du demandeur."""
        self.ensure_one()
        if not self._is_manager_n1():
            raise AccessError(_("Seul le manager N+1 du demandeur peut valider cette demande."))

    def _check_can_process(self):
        self.ensure_one()
        if not self._is_traitement_user():
            raise AccessError(_("Seule une personne de traitement disponible peut traiter cette demande."))

    def _check_can_edit_request(self):
        for rec in self:
            if rec.state != "new":
                raise AccessError(_("La demande ne peut etre modifiee que lorsqu'elle est nouvelle."))
            rec._check_is_demandeur()
        
    # =========================
    # EMAILS WORKFLOW
    # =========================
    def _clean_header(self, value):
        if not value:
            return False
        return str(value).replace("\n", "").replace("\r", "").strip()

    def _get_employee_email(self, emp):
        """Retourne l'email d'un hr.employee (via user/partner)"""
        if not emp:
            return False
        emp = emp.sudo()
        user = emp.user_id
        email = (
            emp.work_email
            or getattr(emp, "private_email", False)
            or (user.partner_id.email if user and user.partner_id else False)
            or (user.email if user else False)
        )
        return self._clean_header(email) if email else False

    def _get_demandeur_email(self):
        self.ensure_one()
        return self._get_employee_email(self.demandeur_id)

    def _get_manager_n1_email(self):
        self.ensure_one()
        return self._get_employee_email(self.manager_n1_id)

    def _get_traiteurs_emails(self):
        """Emails des personnes paramétrées dans ar.fb.traiteur (disponibles)"""
        self.ensure_one()
        emails = set()
        traiteurs = self.env["ar.fb.traiteur"].sudo().search([("disponible", "=", True)])
        for t in traiteurs:
            email = self._get_employee_email(t.employee_id)
            if email:
                emails.add(email)
        return list(emails)

    def _send_template(self, xmlid, email_to_list):
        """Envoi mail template à une liste d'emails."""
        self.ensure_one()
        template = self.env.ref(xmlid, raise_if_not_found=False)
        if not template:
            self.message_post(body=_("Email non envoye : modele introuvable (%s).") % xmlid)
            return

        recipients = [self._clean_header(e) for e in (email_to_list or [])]
        recipients = [e for e in recipients if e]
        recipients = list(dict.fromkeys(recipients))
        if not recipients:
            self.message_post(body=_("Email non envoye : aucun destinataire avec une adresse email renseignee."))
            return

        email_values = {
            "email_to": self._clean_header(",".join(recipients)),
            "reply_to": self._clean_header(self.env.user.partner_id.email or self.env.user.email or ""),
        }
        try:
            template.sudo().send_mail(self.id, force_send=True, raise_exception=True, email_values=email_values)
        except Exception as exc:
            _logger.exception("Erreur d'envoi email fourniture bureau %s via %s", self.name, xmlid)
            self.message_post(body=_("Email non envoye a %s : %s") % (", ".join(recipients), exc))

    def _send_on_state_change(self, old_state, new_state):
        """Règles emails selon ton besoin."""
        self.ensure_one()

        # 1) Création => mail au manager N+1
        if old_state == "new" and new_state == "n1":
            self._send_template(
                "ar_fourniture_bureau.mail_template_fb_new_to_manager",
                [self._get_manager_n1_email()],
            )
            return

        # 2) Validation N+1 => (n1 -> processing)
        if old_state == "n1" and new_state == "processing":
            # 2.1 notifier demandeur (validée)
            self._send_template(
                "ar_fourniture_bureau.mail_template_fb_approved_to_demandeur",
                [self._get_demandeur_email()],
            )
            # 2.2 notifier traiteurs (à traiter)
            self._send_template(
                "ar_fourniture_bureau.mail_template_fb_processing_to_traiteurs",
                self._get_traiteurs_emails(),
            )
            return

        # 3) Réceptionnée => notifier demandeur
        if new_state == "received":
            self._send_template(
                "ar_fourniture_bureau.mail_template_fb_received_to_demandeur",
                [self._get_demandeur_email()],
            )
            return

        # 4) Refusée => notifier demandeur
        if new_state == "refused":
            self._send_template(
                "ar_fourniture_bureau.mail_template_fb_refused_to_demandeur",
                [self._get_demandeur_email()],
            )
            return

    def _post_workflow_trace(self, old_state, new_state):
        self.ensure_one()
        if not old_state or old_state == new_state:
            return

        state_labels = dict(self._fields["state"].selection)
        messages = {
            ("new", "n1"): _("Demande soumise par %s. Demande transmise a Validation N+1."),
            ("n1", "processing"): _("Validation N+1 effectuee par %s. Demande transmise au traitement."),
            ("processing", "received"): _("Traitement cloture par %s. Demande marquee comme livree."),
            ("n1", "refused"): _("Demande refusee par %s."),
            ("processing", "refused"): _("Demande refusee par %s."),
        }
        body = messages.get((old_state, new_state))
        if body:
            body = body % self.env.user.name
        else:
            body = _("Changement d'etape effectue par %s : %s -> %s.") % (
                self.env.user.name,
                state_labels.get(old_state, old_state),
                state_labels.get(new_state, new_state),
            )
        self.message_post(body=body)

    date_besoin = fields.Date(string="Date de besoin", required=True, tracking=True)

    line_ids = fields.One2many(
        "ar.fb.demande.line",
        "demande_id",
        string="Articles demandés",
        copy=True
    )

    commentaire = fields.Text(string="Commentaire", tracking=True)

    
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "ar_fb_demande_ir_attachment_rel",
        "demande_id",
        "attachment_id",
        string="Pièces jointes",
        tracking=True,
    )

   
    compressed_attachment_ids = fields.Many2many(
        "ir.attachment",
        "ar_fb_demande_ir_attachment_gz_rel",
        "demande_id",
        "attachment_id",
        string="Pièces jointes compressées (tech)",
        readonly=True,
        copy=False,
    )

    
    def _extract_added_m2m_ids(self, current_ids, commands):
        if not commands:
            return []

        current = set(current_ids)
        added = set()

        for cmd in commands:
            if not isinstance(cmd, (list, tuple)) or not cmd:
                continue

            op = cmd[0]

            if op == 4 and len(cmd) > 1 and cmd[1]:
                if cmd[1] not in current:
                    added.add(cmd[1])

            elif op == 6 and len(cmd) > 2 and cmd[2]:
                new_set = set(cmd[2])
                added |= (new_set - current)

            

        return list(added)

    # -----------------------------
    # Compression: copie gzip
    # -----------------------------
    def _should_compress(self, attachment):
        mimetype = (attachment.mimetype or "").lower()
        return mimetype == "application/pdf" or mimetype.startswith("image/")

    def _ensure_compressed_copy(self, attachment):
        """
        Crée une copie .gz pour PDF/images, sans toucher l'original.
        => téléchargement normal garanti.
        Compression TOUJOURS (petit ou grand, gain ou pas).
        """
        self.ensure_one()

        if not attachment or not attachment.datas:
            return

        if not self._should_compress(attachment):
            return

        marker = f"GZ_OF:{attachment.id}"

        
        existing = self.env["ir.attachment"].search([
            ("res_model", "=", self._name),
            ("res_id", "=", self.id),
            ("description", "=", marker),
        ], limit=1)
        if existing:
            if existing.id not in self.compressed_attachment_ids.ids:
                self.compressed_attachment_ids = [(4, existing.id)]
            return

        raw = base64.b64decode(attachment.datas)
        gz = gzip.compress(raw, compresslevel=9)

        gz_name = (attachment.name or "file") + ".gz"

        gz_att = self.env["ir.attachment"].create({
            "name": gz_name,
            "type": "binary",
            "datas": base64.b64encode(gz),
            "mimetype": "application/gzip",
            "res_model": self._name,
            "res_id": self.id,
            "description": marker,
        })

        self.compressed_attachment_ids = [(4, gz_att.id)]

    def _compress_attachments(self, attachment_ids=None):
        self.ensure_one()
        atts = self.env["ir.attachment"].browse(attachment_ids) if attachment_ids else self.attachment_ids
        for att in atts:
            self._ensure_compressed_copy(att)

    # -----------------------------
    # create / write / fix
    # -----------------------------

    def _fix_attachment_ownership(self):
        for record in self:
            for att in record.attachment_ids | record.compressed_attachment_ids:
                att.write({
                    "res_model": record._name,
                    "res_id": record.id,
                })
        return self


    @api.model_create_multi
    def create(self, vals_list):
        employee_model = self.env["hr.employee"]
        sequence_model = self.env["ir.sequence"]
        current_user = self.env.user

        emp = employee_model.search([("user_id", "=", current_user.id)], limit=1)
        if not emp:
            raise AccessError(_("Aucun employe n'est lie a votre utilisateur. Vous ne pouvez pas creer une demande."))

        for vals in vals_list:
            # Auto-fill demandeur
            if not vals.get("demandeur_id") and emp:
                vals["demandeur_id"] = emp.id
            elif vals.get("demandeur_id") != emp.id:
                raise AccessError(_("Vous ne pouvez creer une demande que pour vous-meme."))

            # Séquence
            if vals.get("name", "Nouveau") == "Nouveau":
                vals["name"] = sequence_model.next_by_code("ar.fb.demande") or "DEM"

        records = super().create(vals_list)

        for rec in records:
            if not rec.line_ids:
                raise ValidationError(_("Veuillez ajouter au moins une ligne (Article / Quantité)."))

            # Fix ownership des pièces jointes originales
            rec._fix_attachment_ownership()

            # Compression des pièces jointes
            rec._compress_attachments()

            # Fix ownership aussi pour les pièces jointes compressées créées
            rec._fix_attachment_ownership()

            rec._send_on_state_change(False, rec.state)

        return records

    def write(self, vals):
        if not self.env.context.get("ar_fb_skip_acl_check"):
            state_only = set(vals) == {"state"}
            if not state_only:
                self._check_can_edit_request()
            elif "state" in vals:
                for rec in self:
                    new_state = vals["state"]
                    if rec.state == "new" and new_state == "n1":
                        rec._check_is_demandeur()
                    elif rec.state == "n1" and new_state == "processing":
                        rec._check_is_manager_n1()
                    elif rec.state == "n1" and new_state == "refused":
                        rec._check_is_manager_n1()
                    elif rec.state == "processing" and new_state in ("received", "refused"):
                        rec._check_can_process()
                    elif rec.state != new_state:
                        raise AccessError(_("Transition de statut non autorisee."))

        # Pour détecter changement d'état
        old_states = {rec.id: rec.state for rec in self}

        new_ids_by_rec = {}
        if "attachment_ids" in vals:
            for rec in self:
                new_ids_by_rec[rec.id] = rec._extract_added_m2m_ids(
                    rec.attachment_ids.ids,
                    vals.get("attachment_ids")
                )

        res = super().write(vals)

        # Fix ownership des pièces jointes après write
        if "attachment_ids" in vals or "compressed_attachment_ids" in vals:
            self._fix_attachment_ownership()

        # Compression des nouvelles pièces jointes ajoutées
        if "attachment_ids" in vals:
            for rec in self:
                added = new_ids_by_rec.get(rec.id) or []
                rec._compress_attachments(added or None)

            # Re-fix après création des copies compressées
            self._fix_attachment_ownership()

        # Emails si state change
        if "state" in vals:
            for rec in self:
                old_state = old_states.get(rec.id)
                new_state = rec.state
                if old_state != new_state:
                    rec._send_on_state_change(old_state, new_state)
                    rec._post_workflow_trace(old_state, new_state)

        return res

    # -----------------------------
    # Constraints + workflow
    # -----------------------------
    @api.constrains("line_ids")
    def _check_lines(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_("La demande doit contenir au moins une ligne."))
            for l in rec.line_ids:
                if l.quantity <= 0:
                    raise ValidationError(_("La quantité doit être supérieure à 0."))

    def action_submit_n1(self):
        for rec in self:
            if rec.state != "new":
                continue
            rec._check_is_demandeur()
            if not rec.manager_n1_id or not rec.manager_n1_id.user_id:
                raise ValidationError(_("Aucun manager N+1 n'est defini pour le demandeur."))
            rec.write({"state": "n1"})

    def action_approve_n1(self):
        for rec in self:
            if rec.state != "n1":
                continue
            rec._check_is_manager_n1()
            rec.write({"state": "processing"})

    def action_refuse(self):
        for rec in self:
            if rec.state in ("received", "refused"):
                continue

            
            if rec.state == "n1":
                rec._check_is_manager_n1()

            
            elif rec.state == "processing":
                rec._check_can_process()

            
            rec.write({"state": "refused"})

    def action_received(self):
        for rec in self:
            if rec.state != "processing":
                continue
            rec._check_can_process()
            rec.write({"state": "received"})


class ARFBDemandeLine(models.Model):
    _name = "ar.fb.demande.line"
    _description = "Ligne demande fourniture"
    _order = "id asc"

    demande_id = fields.Many2one("ar.fb.demande", string="Demande", required=True, ondelete="cascade")
    article_id = fields.Many2one("ar.fb.article", string="Article", required=True)
    quantity = fields.Integer(string="Quantité", required=True, default=1)

    @api.model_create_multi
    def create(self, vals_list):
        demandes = self.env["ar.fb.demande"].browse([
            vals["demande_id"] for vals in vals_list if vals.get("demande_id")
        ])
        demandes._check_can_edit_request()
        return super().create(vals_list)

    def write(self, vals):
        self.mapped("demande_id")._check_can_edit_request()
        return super().write(vals)

    def unlink(self):
        self.mapped("demande_id")._check_can_edit_request()
        return super().unlink()
