{
    'name': 'Delivery Management',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Manage product deliveries and receipts',
    'author': 'Odoo Community',
    'depends': ['base', 'stock', 'sale', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/delivery_management_view.xml',
        'views/thesis_management_view.xml',
        'views/thesis_topic_view.xml',
        'views/student_management_view.xml',
        'data/delivery_data.xml',
    ],
    'installable': True,
    'application': True,
    'icon': '/delivery_management/static/description/icon.png',
}
