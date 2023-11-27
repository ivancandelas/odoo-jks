
from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _sale_order_list(self):
        self.ensure_one()
        return [x.strip() for x in self.origin.split(',')]

    def origin_sales_orders(self):
        self.ensure_one()
        sale_order_list = self._sale_order_list()
        return self.env['sale.order'].search([('name', 'in', sale_order_list)])
