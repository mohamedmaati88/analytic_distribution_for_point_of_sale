from odoo import models

_PL_TYPES = frozenset({
    'income',
    'income_other',
    'expense',
    'expense_depreciation',
    'expense_direct_cost',
})


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def action_pos_order_invoice(self):
        result = super().action_pos_order_invoice()
        for order in self:
            config = order.session_id.config_id
            if not config._analytic_applicable():
                continue
            distribution = config._get_analytic_distribution()
            invoice = (
                getattr(order, 'account_move', None)
                or getattr(order, 'invoice_id', None)
            )
            if not invoice and isinstance(result, dict):
                inv_id = result.get('res_id')
                domain = result.get('domain')
                if inv_id:
                    invoice = self.env['account.move'].browse(inv_id)
                elif domain:
                    invoice = self.env['account.move'].search(domain, limit=1)
            if invoice:
                _write_analytic(invoice, distribution)
        return result

    def _generate_pos_order_invoice(self):
        result = super()._generate_pos_order_invoice()
        config = self.session_id.config_id
        if config._analytic_applicable():
            distribution = config._get_analytic_distribution()
            invoice = (
                getattr(self, 'account_move', None)
                or getattr(self, 'invoice_id', None)
            )
            if invoice:
                _write_analytic(invoice, distribution)
        return result


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    def _prepare_invoice_line(self, **kwargs):
        vals = super()._prepare_invoice_line(**kwargs)
        config = self.order_id.session_id.config_id
        if config._analytic_applicable():
            distribution = config._get_analytic_distribution()
            if distribution:
                vals['analytic_distribution'] = distribution
        return vals


def _write_analytic(invoice, distribution):
    lines = invoice.line_ids.filtered(
        lambda l: l.account_id.account_type in _PL_TYPES
    )
    if lines:
        lines.sudo().write({'analytic_distribution': distribution})
