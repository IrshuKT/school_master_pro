/** @odoo-module **/
import { registry } from "@web/core/registry";

function backButtonReplace(env, action) {
    const winAction = action.params.action;
    console.log("✅ Back to root:", winAction);
    return env.services.action.doAction(winAction, {
        clearBreadcrumbs: true,   // 🔑 wipes entire stack
    });
}

registry.category("actions").add("do-action-replace-history", backButtonReplace);
