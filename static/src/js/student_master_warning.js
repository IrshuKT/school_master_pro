/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { onMounted, onPatched } from "@odoo/owl";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    setup() {
        super.setup();
        this.notification = useService("notification");
        this._warnedFor = {};  // track which fields we already warned for

        const checkAndWarn = () => {
    const root = this.model?.root;
    if (!root || root.resModel !== "student.master") return;

    const currentId = root.resId;
    const data = root.data || {};

    // Skip new records (unsaved)
    if (!currentId) {
        return;
    }

      // University reg check
    if ((!data.reg_no || !data.reg_no.trim()) &&
        this._warnedFor[currentId] !== "reg_no") {
        this.notification.add(
            _t("⚠ Update Registration Status."),
            { type: "warning" }
        );
        this._warnedFor[currentId] = "reg_no";
    }

    // Aadhaar check
    if ((!data.aadhaar_card || !data.aadhaar_card.trim()) &&
        this._warnedFor[currentId] !== "aadhaar") {
        this.notification.add(
            _t("⚠ Update Aadhaar Card."),
            { type: "warning" }
        );
        this._warnedFor[currentId] = "aadhaar";
    }

    // Phone check
    if ((!data.student_contact1 || !data.student_contact1.trim()) &&
        this._warnedFor[currentId] !== "phone") {
        this.notification.add(
            _t("⚠ Update Mobile number."),
            { type: "warning" }
        );
        this._warnedFor[currentId] = "phone";
    }
};


        onMounted(checkAndWarn);
        onPatched(checkAndWarn);
    },
});
