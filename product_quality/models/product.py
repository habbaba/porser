# -*- coding: utf-8 -*-
from odoo import fields, models, _


class ProductQuality(models.Model):
    _name = 'product.quality'

    name = fields.Char(string='Name', required=True)
    quality_code = fields.Char(string='Code', required=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_quality_ids = fields.One2many('product.template', 'product_quality_id')
    product_quality_id = fields.Many2one('product.template')
    quality_id = fields.Many2one('product.quality', ondelete='restrict')

    def action_create_product_quality(self):
        self.ensure_one()

        qualities = self.env['product.quality'].search([])
        quality_ids = self.product_quality_ids.mapped('quality_id').ids

        for quality in qualities:
            if quality.id in quality_ids:
                continue

            product = self.copy()
            product.write({
                'name': f"{self.name} ({quality.name} - {quality.quality_code})",
                'product_quality_id': self.id,
                'quality_id': quality.id,
                'list_price': self.list_price,
                'standard_price': self.standard_price,
                'categ_id': self.categ_id.id,
                'default_code': f"{self.default_code}-{quality.quality_code}",
            })
        for product in self.product_quality_ids.mapped('product_variant_id.product_tmpl_id'):
            mrp = self.env['mrp.bom'].search([('product_tmpl_id', '=', product.id)])
            if not mrp:
                self.env['mrp.bom'].create({
                    'product_tmpl_id': product.id,
                    'bom_line_ids': [(0, 0, {'product_id': self.product_variant_id.id})]
                })
class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    first_quality_ids = fields.One2many('mrp.product.quality.next', 'first_quality_id')

    def action_quality_movements(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.product.quality.next',
            'view_mode': 'tree',
            'domain': [('first_quality_id', '=', self.id)],
            'target': 'new',
            'name': _('Quality Movements')
        }

    def action_generate_quality_product(self):
       return {
            'type': 'ir.actions.act_window',
            'res_model': 'separate.by.quality',
            'view_mode': 'form',
            'target': 'new',
            'name': _('Filtered Quality')
        }
    
class MrpProductionNext(models.Model):
    _name="mrp.product.quality.next"

    first_quality_id = fields.Many2one('mrp.production')

    next_id = fields.Many2one('mrp.production')
    quality_code = fields.Char(string='Code', required=True)
    product_qty = fields.Float(string='Quantity', required=True)
    
class FilteredQuality(models.TransientModel):
    _name = 'separate.by.quality'

    quality_id = fields.Many2one('product.quality', string='Quality', required=True)
    product_qty = fields.Float(string='Quantity', required=True)

    def action_separate_by_quality(self):
        self.ensure_one()
        mrp = self.env['mrp.production'].browse(self._context.get('active_id'))
        product = mrp.product_id.product_tmpl_id.product_quality_ids.filtered(lambda x: x.quality_id.id == self.quality_id.id)
        if product:
            bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', product.id)])
            production = self.env['mrp.production'].create({
                'product_id': product.product_variant_id.id,
                'product_qty': self.product_qty,
                'product_uom_id': product.uom_id.id,
                'bom_id': bom.id,
                'qty_producing': self.product_qty,
                'product_tmpl_id': product.id,
            })
            production._onchange_company_id()
            production._onchange_product_id()
            production._onchange_product_qty()
            production._onchange_bom_id()
            production._onchange_date_planned_start()
            production._onchange_move_raw()
            production._onchange_move_finished_product()
            production._onchange_move_finished()
            production._onchange_location()
            production._onchange_location_dest()
            production._onchange_picking_type()
            production._onchange_producing()
            production._onchange_lot_producing()
            production._onchange_workorder_ids()
            production.action_confirm()
            production.with_context(skip_immediate = True).button_mark_done()

            mrp.write({
                'first_quality_ids' : [(0, 0, {'next_id' : production.id, 'quality_code': production.id, 'product_qty': production.product_qty})]
            })

            # return {
            #     'type': 'ir.actions.act_window',
            #     'res_model': 'mrp.production',
            #     'view_mode': 'form',
            #     'res_id': production.id,
            #     'target': 'current',
            #     'name': _('Production Order')
            # }