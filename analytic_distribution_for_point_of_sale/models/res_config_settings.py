from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_analytic_line_ids = fields.One2many(
        comodel_name='pos.config.analytic.line',
        related='pos_config_id.analytic_line_ids',
        readonly=False,
    )
