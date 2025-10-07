/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { useService } from "@web/core/utils/hooks";
import { onMounted, useEffect, useRef, onWillUnmount, useState } from "@odoo/owl";

patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        this.dialog = useService("dialog");
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this._draftDialogShown = useRef(false);
        this._retryTimeout = useRef(null);
        this.retryCount = useState({ value: 0 }); // Track retry attempts

        // Run once when form is opened
        onMounted(() => {
            this._scheduleFirstReminder();
        });

        // Also run if user navigates to another record via Next/Previous
        useEffect(
            () => {
                // Reset and restart reminders when record changes
                this._resetReminders();
                this._scheduleFirstReminder();
            },
            () => [this.model.root?.resId, this.model.root?.data?.state]
        );

        // Clean up timeout when component unmounts
        onWillUnmount(() => {
            this._resetReminders();
        });
    },

    _resetReminders() {
        // Clear any existing timeout
        if (this._retryTimeout.value) {
            clearTimeout(this._retryTimeout.value);
            this._retryTimeout.value = null;
        }
        // Reset flags and counters
        this._draftDialogShown.value = false;
        this.retryCount.value = 0;
    },

    _scheduleFirstReminder() {
        const record = this.model.root;

        // Check conditions for showing dialog
        if (!record?.resId || record.data?.state !== "draft") {
            return;
        }

        console.log("Scheduling first reminder in 1 minute...");

        // Schedule first reminder after 1 minute (60,000 milliseconds)
        this._retryTimeout.value = setTimeout(() => {
            this._showDraftWarning();
        }, 60000); // 1 minute = 60,000 milliseconds
    },

    async _showDraftWarning() {
        const record = this.model.root;

        // Check conditions for showing dialog
        if (!record?.resId || record.data?.state !== "draft") {
            return;
        }

        // Increment retry count
        this.retryCount.value++;

        // Reset the flag to allow showing dialog
        this._draftDialogShown.value = false;

        // Mark as shown to prevent multiple dialogs in same session
        this._draftDialogShown.value = true;

        // Show dialog
        this._showConfirmationDialog(record);
    },

    _showConfirmationDialog(record) {
        const isFirstReminder = this.retryCount.value === 1;
        const title = isFirstReminder ?
            "⚠️ Record in Draft State" :
            `⚠️ Record Still in Draft (Reminder ${this.retryCount.value})`;

        const body = isFirstReminder ?
            "This record has been in DRAFT state.\n\nWould you like to CONFIRM it now?" :
            `This record has been in DRAFT state.\n\nWould you like to CONFIRM it now?`;

        this.dialog.add(ConfirmationDialog, {
            title: title,
            body: body,
            confirmLabel: "✅ Confirm Record",
            cancelLabel: `✋ Keep as Draft ${isFirstReminder ? '(Remind )' : '(Remind)'}`,
            confirm: async () => {
                try {
                    await this.orm.call(
                        record.resModel,
                        "action_save",
                        [[record.resId]]
                    );
                    // Update the record state in the form
                    record.update({
                        state: "confirmed",
                        is_locked: true
                    });
                    // Show success feedback
                    this.notification.add(
                        "Record confirmed successfully!",
                        { type: "success" }
                    );
                    // Clear any pending retry timeout since record is now confirmed
                    this._resetReminders();
                    console.log("Record confirmed - reminders stopped");
                } catch (error) {
                    console.error("Failed to confirm record:", error);
                    this.notification.add(
                        "Failed to confirm record. Please try again.",
                        { type: "danger" }
                    );
                    // Schedule retry even if confirmation fails
                    this._scheduleNextReminder();
                }
            },
            cancel: () => {
                // User chose to keep as draft - schedule next reminder
                console.log(`User chose to keep as draft - will remind in 2 minutes (Reminder ${this.retryCount.value})`);
                this._scheduleNextReminder();
            },
            onClose: () => {
                // If dialog is closed without choosing, also schedule next reminder
                if (record.data?.state === "draft") {
                    this._scheduleNextReminder();
                }
            },
        });
    },

    _scheduleNextReminder() {
        const record = this.model.root;

        // Check if record still exists and is still draft
        if (!record?.resId || record.data?.state !== "draft") {
            return;
        }

        // Clear any existing timeout
        if (this._retryTimeout.value) {
            clearTimeout(this._retryTimeout.value);
        }

        // Schedule next reminder after 2 minutes (120,000 milliseconds)
        this._retryTimeout.value = setTimeout(() => {
            console.log(`2 minutes passed - showing draft reminder ${this.retryCount.value + 1}`);
            this._draftDialogShown.value = false; // Reset flag to allow showing again
            this._showDraftWarning(); // Show the dialog again
        }, 120000); // 2 minutes = 120,000 milliseconds
    }
});