
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def update_analytic_lines(self, product_id, cost, discount):
        for sale_order in self:
            if sale_order.analytic_account_id:
                _logger.info("[***] Updating analytic account fo sale order '%s'", sale_order.name)
                for invoice in sale_order.invoice_ids:
                    invoice.update_lines_cost(product_id, cost, discount)
            else:
                _logger.info("[***] Sale order has no analytic account")

