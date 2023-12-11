
from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _sale_order_list(self):
        self.ensure_one()
        order_list = []
        if self.origin:
            order_list = [x.strip() for x in self.origin.split(',')]
        return order_list

    def origin_sales_orders(self):
        self.ensure_one()
        sale_order_list = self._sale_order_list()
        return self.env['sale.order'].search([('name', 'in', sale_order_list)])
