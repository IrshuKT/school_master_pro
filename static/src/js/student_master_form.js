/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { registry } from "@web/core/registry";

class StudentMasterFormController extends FormController {
    setup() {
        super.setup();
        this.on('update', () => this._updateButtonVisibility());
    }

    _updateButtonVisibility() {
        const isEditMode = this.model.root.isEditing;
        const saveButton = this.el.querySelector('button[name="save_student"]');
        const editButton = this.el.querySelector('button[name="edit_student"]');
        const deleteButton = this.el.querySelector('button[name="delete_student"]');

        if (saveButton) {
            saveButton.classList.toggle('d-none', !isEditMode);
        }
        if (editButton) {
            editButton.classList.toggle('d-none', isEditMode);
        }
        if (deleteButton) {
            deleteButton.classList.toggle('d-none', isEditMode);
        }
    }
}

registry.category("view_controllers").add("student_master_form", {
    Controller: StudentMasterFormController,
    viewTypes: ["form"],
    model: "student.master",
});