from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PosConfigAnalyticLine(models.Model):
    _name = 'pos.config.analytic.line'
    _description = 'POS Analytic Distribution Line'
    _order = 'id'

    config_id = fields.Many2one(
        comodel_name='pos.config',
        required=True,
        ondelete='cascade',
    )
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        required=True,
    )
    percentage = fields.Float(
        string='%',
        default=100.0,
        digits=(5, 2),
    )

    @api.constrains('percentage')
    def _check_percentage(self):
        for rec in self:
            if not (0 < rec.percentage <= 100):
                raise ValidationError(
                    self.env._('Percentage must be between 0.01 and 100.')
                )

