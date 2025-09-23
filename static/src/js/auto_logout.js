/** @odoo-module **/

console.log("Auto logout module loaded");

const IDLE_TIMEOUT = 30 * 60 * 1000; // 30s for testing

function setupAutoLogout() {
    console.log("Auto logout started");

    let lastActivity = Date.now();

    const resetTimer = () => {
        lastActivity = Date.now();
        console.log("Activity detected, timer reset");
    };

    ["click", "mousemove", "keypress"].forEach(evt => {
        document.addEventListener(evt, resetTimer);
    });

    window.setInterval(() => {
        if (Date.now() - lastActivity > IDLE_TIMEOUT) {
            console.log("Logging out due to inactivity");
            // ✅ no session.logout(), just redirect
            window.location = "/web/session/logout";
        }
    }, 1000);
}

document.addEventListener("DOMContentLoaded", () => {
    console.log("Initializing auto logout");
    setupAutoLogout();
});
