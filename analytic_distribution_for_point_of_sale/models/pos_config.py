from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    use_analytic_accounts = fields.Boolean(
        string='Analytic Accounts',
        default=False,
    )
    analytic_line_ids = fields.One2many(
        comodel_name='pos.config.analytic.line',
        inverse_name='config_id',
        string='Analytic Distribution',
    )
    analytic_accounting_active = fields.Boolean(
        compute='_compute_analytic_accounting_active',
        store=False,
    )

    @api.depends_context('uid')
    def _compute_analytic_accounting_active(self):
        active = self.env.user.has_group(
            'analytic.group_analytic_accounting'
        ) or self.env.user.has_group('account.group_account_analytic')
        for rec in self:
            rec.analytic_accounting_active = active

    def action_apply_analytic_to_history(self):
        self.ensure_one()
        wizard = self.env['pos.analytic.history.wizard'].create(
            {'config_id': self.id}
        )
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Apply Analytic to History'),
            'res_model': 'pos.analytic.history.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _analytic_applicable(self):
        return (
            self.use_analytic_accounts
            and bool(self.analytic_line_ids)
            and (
                self.env.user.has_group('analytic.group_analytic_accounting')
                or self.env.user.has_group('account.group_account_analytic')
            )
        )

    def _get_analytic_distribution(self):
        return {
            str(line.analytic_account_id.id): line.percentage
            for line in self.analytic_line_ids
            if line.analytic_account_id and line.percentage
        }
