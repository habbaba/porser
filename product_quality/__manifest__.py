# -*- coding: utf-8 -*-
# Copyright © 2022 Projet (https://bulutkobi.io)
# Part of Bulutkobi License. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product: Quality',
    'version': '1.0',
    'author': 'Projet',
    'website': 'https://bulutkobi.io',
    'license': 'LGPL-3',
    'sequence': 1455,
    'category': 'Sales/Products',
    'depends': [
        'mrp',
    ],
    'data': [
        'views/product.xml',
        'views/mrp_production.xml',
        'security/ir.model.access.csv'
    ],
    'application': False,
    'auto_install': False,
}
