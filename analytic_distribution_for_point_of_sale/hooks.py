def post_uninstall_hook(env):
    """
    Clean up analytic distribution data set by this module on pos.config records.
    Resets the use_analytic_accounts flag so no orphaned setting remains.
    account.move.line.analytic_distribution is a native Odoo field — its data
    is intentionally preserved after uninstall.
    """
    try:
        env['pos.config'].search([('use_analytic_accounts', '=', True)]).write(
            {'use_analytic_accounts': False}
        )
    except Exception:
        pass
