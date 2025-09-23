# -*- coding: utf-8 -*-
{
    'name': "School Master Pro",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Irshad K T",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'School',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/teacher_login.xml',
        'data/receipt_sequence.xml',
        'data/roll_number_sequence.xml',
        'data/student_fee_cron.xml',
        'report/student_ledger_report.xml',
        'report/print_icon.xml',
        'views/student_exam_result.xml',
        'views/teacher_view.xml',
        'views/student_master.xml',
        'views/error.action.message.xml',
        'views/teacher_master.xml',
        'views/settings.xml',
        'views/student_fee_receipt.xml',
        'views/student_fee_invoice.xml',
        'views/student_ledger.xml',
        'views/student_courses.xml',
        'views/student_documents_collection.xml',
        'views/fee_update_wizard.xml',
        'views/student_concession_wizard.xml',
        'views/finance_balance.xml',
        'views/finance_head.xml',
        'views/finance_vouchers.xml',
        # 'data/student_card_print.xml',
        'views/all_menu.xml',
        'views/back_button.xml',

    ],

    'assets': {
        'web.assets_backend': [

            # 'school_master/static/src/js/student_warining_okbutton.js',
            'school_master_pro/static/src/js/student_master_warning.js',
            'school_master_pro/static/src/js/teacher_autosave.js',
            'school_master_pro/static/src/js/back_button_patch.js',
            'school_master_pro/static/src/js/student_master_kanban.js',
            # 'school_master/static/src/js/cancel_button.js',
            #'school_master/static/src/js/auto_logout.js',
            'school_master_pro/static/src/css/student_master.css',
            # 'school_master_pro/static/src/css/hide_form_icon.css',

        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'license': 'LGPL-3'
}
