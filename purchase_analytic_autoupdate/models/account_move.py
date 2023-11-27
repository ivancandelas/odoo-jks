
import logging

from odoo import models

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Actualiza los valores de la cuenta analitica aun si no ha ingresado el producto
    def action_post(self):
        res = super(AccountMove, self).action_post()

        if res:
            for move in self:
                _logger.info("[***] Updating analityc account")

                if move.type == 'in_invoice' and move.invoice_origin:
                    _logger.info("[***] Searching purchase order")
                    purchase_orders = self.env['purchase.order'].search([('name', '=', move.invoice_origin)])
                    invoice_lines = move.invoice_line_ids
                    for inv_line in invoice_lines:
                        for purchase_order in purchase_orders:
                            sale_orders = purchase_order.origin_sales_orders()
                            for sale_order in sale_orders:
                                sale_order.update_analytic_lines(inv_line.product_id, inv_line.price_unit, inv_line.discount)
                else:
                    _logger.info("[***] Not purchase invoice, nothing to do")

        return res

    def update_lines_cost(self, product_id, cost, discount):
        self.ensure_one()
        _logger.info("[***] Updating line '%s' '%s'", product_id, cost)

        account_id = product_id.product_tmpl_id.property_account_expense_id

        if not account_id:
            account_id = product_id.product_tmpl_id.categ_id.property_account_expense_categ_id

        account_output_id = product_id.product_tmpl_id.categ_id.property_stock_account_output_categ_id

        to_write = []
        expense_lines = self.line_ids.filtered(lambda move: move.exclude_from_invoice_tab == True and move.account_id == account_id and move.product_id == product_id)
        for exp_line in expense_lines:
            exp_line.product_id.standard_price = cost - 0.0 if not discount else (cost * (1.0/discount))
            to_write.append((1, exp_line.id, {
                        'price_unit': cost * -1,
                        'discount': discount,
                    }))
            for analytic in exp_line.analytic_line_ids:
                analytic.on_change_unit_amount()

        output_lines = self.line_ids.filtered(lambda move: move.exclude_from_invoice_tab == True and move.account_id == account_output_id and move.product_id == product_id)
        for out_line in output_lines:
            to_write.append((1, out_line.id, {
                        'price_unit': cost,
                        'discount': discount,
                    }))

        self.write({'line_ids': to_write})

