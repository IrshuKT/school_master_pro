/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { onMounted, onPatched } from "@odoo/owl";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    setup() {
        super.setup();
        this.dialog = useService("dialog");
        this._warnedForAadhaar = null;
        this._warnedForContact = null;

        const checkAndWarn = () => {
            const root = this.model?.root;
            if (!root || root.resModel !== "student.master") return;

            const currentId = root.resId;
            const aadhaarVal = (root.data?.aadhaar_card || "").trim();
            const contactVal = (root.data?.student_contact1 || "").trim();

            // Check for missing Aadhaar
            if (!aadhaarVal && this._warnedForAadhaar !== currentId) {
                const msg = _t("⚠ Aadhaar Card Number is missing.");
                console.log(">>> Aadhaar Warning:", msg);

                setTimeout(() => {
                    confirm(msg);
                }, 100);

                this._warnedForAadhaar = currentId;
            }

            // Check for missing Contact Number
            if (!contactVal && this._warnedForContact !== currentId) {
                const msg = _t("⚠ Contact Number is missing.");
                console.log(">>> Contact Warning:", msg);

                setTimeout(() => {
                    confirm(msg);
                }, 100);

                this._warnedForContact = currentId;
            }
        };

        onMounted(checkAndWarn);
        onPatched(checkAndWarn);
    },
});