from odoo import models

_PL_TYPES = frozenset({
    'income',
    'income_other',
    'expense',
    'expense_depreciation',
    'expense_direct_cost',
})


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _validate_session(self, balancing_account=False, amount_to_balance=0,
                          bank_payment_method_diffs=None):
        result = super()._validate_session(
            balancing_account=balancing_account,
            amount_to_balance=amount_to_balance,
            bank_payment_method_diffs=bank_payment_method_diffs,
        )
        config = self.config_id
        if config._analytic_applicable() and self.move_id:
            distribution = config._get_analytic_distribution()
            lines = self.move_id.line_ids.filtered(
                lambda l: l.account_id.account_type in _PL_TYPES
            )
            if lines:
                lines.sudo().write({'analytic_distribution': distribution})
        return result
