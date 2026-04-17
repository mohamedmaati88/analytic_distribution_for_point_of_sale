from odoo import fields, models

_PL_TYPES = frozenset({
    'income',
    'income_other',
    'expense',
    'expense_depreciation',
    'expense_direct_cost',
})


class PosAnalyticHistoryWizard(models.TransientModel):
    _name = 'pos.analytic.history.wizard'
    _description = 'POS Analytic Distribution — Backfill'

    config_id = fields.Many2one(
        comodel_name='pos.config',
        required=True,
        ondelete='cascade',
    )
    mode = fields.Selection(
        selection=[
            ('replace', 'Replace existing analytic distribution'),
            ('add', 'Add with existing analytic distribution'),
        ],
        default='replace',
        required=True,
        string='Mode',
    )

    def action_apply(self):
        self.ensure_one()
        distribution = self.config_id._get_analytic_distribution()
        if not distribution:
            return {'type': 'ir.actions.act_window_close'}

        moves = self._collect_moves()
        if not moves:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': self.env._('No Entries Found'),
                    'message': self.env._(
                        'No accounting entries found for this POS configuration.'
                    ),
                    'type': 'warning',
                },
            }

        pl_lines = moves.mapped('line_ids').filtered(
            lambda l: l.account_id.account_type in _PL_TYPES
        )

        if self.mode == 'replace':
            pl_lines.sudo().write({'analytic_distribution': distribution})
        else:
            for line in pl_lines:
                merged = dict(line.analytic_distribution or {})
                merged.update(distribution)
                line.sudo().write({'analytic_distribution': merged})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': self.env._('Done'),
                'message': self.env._(
                    'Analytic distribution applied to %d line(s).', len(pl_lines)
                ),
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def _collect_moves(self):
        Move = self.env['account.move']
        config_id = self.config_id.id

        moves = self.env['pos.session'].search(
            [('config_id', '=', config_id), ('move_id', '!=', False)]
        ).mapped('move_id')

        if 'pos_order_ids' in Move._fields:
            moves |= Move.search([
                ('pos_order_ids.config_id', '=', config_id),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
            ])
        else:
            orders = self.env['pos.order'].search(
                [('config_id', '=', config_id)]
            )
            for order in orders:
                inv = (
                    getattr(order, 'account_move', None)
                    or getattr(order, 'invoice_id', None)
                )
                if inv and inv.id:
                    moves |= inv

        return moves
