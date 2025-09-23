odoo.define('school_master_pro.teacher_form', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var Dialog = require('web.Dialog');

    FormController.include({
        // Disable autosave for teacher.master
        _update: function (record, options) {
            if (this.modelName === 'teacher.master') {
                // Prevent autosave entirely
                return Promise.resolve();
            }
            return this._super.apply(this, arguments);
        },

        // Block default save action (Ctrl+S or breadcrumb save)
        saveRecord: function () {
            if (this.modelName === 'teacher.master') {
                Dialog.alert(this, "Please use the 'Confirm' button to save changes.");
                return Promise.resolve();
            }
            return this._super.apply(this, arguments);
        }
    });
});