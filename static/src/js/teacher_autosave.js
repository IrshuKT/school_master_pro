/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { useService } from "@web/core/utils/hooks";
import { onMounted, useEffect } from "@odoo/owl";

patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        this.dialog = useService("dialog");
        this.orm = useService("orm");
        this.action = useService("action");

        // Run once when form is opened
        onMounted(() => {
            this._showDraftWarning();
        });

        // Also run if user navigates to another record via Next/Previous
        useEffect(
            () => {
                this._showDraftWarning();
            },
            () => [this.model.root?.resId, this.model.root?.data?.state]
        );
    },

    _showDraftWarning() {
    const record = this.model.root;
    if (!record.resId || record.data?.state !== "draft" || this._draftDialogShown) {
        return;
    }
    this._draftDialogShown = true;

    this.dialog.add(ConfirmationDialog, {
        title: "⚠️ Record still not Confirmed",
        body: "This record is still in DRAFT.\n\n👉 Would you like to CONFIRM it now?",
        confirmLabel: "✅ Confirm",
        cancelLabel: "❌ Keep as Draft",
        confirm: async () => {
            await this.orm.call(record.resModel, "action_save", [[record.resId]]);
            record.update({ state: "confirmed", is_locked: true });
        },
        cancel: () => {},
    });
}

});
