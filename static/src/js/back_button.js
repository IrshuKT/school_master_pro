odoo.define('school_master_pro.back_button', function (require) {
    "use strict";

    const FormController = require('web.FormController');
    const viewRegistry = require('web.view_registry');
    const FormView = require('web.FormView');

    const CustomFormController = FormController.extend({
        buttons_template: 'school_master_pro.FormViewButtons',

        _onBackButtonClick: function () {
            window.history.back();  // Or use this.do_action(...) to go to tree view
        },

        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.$buttons) {
                this.$buttons.find('.o_back_button').on('click', this._onBackButtonClick.bind(this));
            }
        },
    });

    viewRegistry.add('custom_form_view', FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: CustomFormController,
        }),
    }));
});
