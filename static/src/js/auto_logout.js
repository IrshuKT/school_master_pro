/** @odoo-module **/

console.log("🚀 Auto logout module loaded and working");

const IDLE_TIMEOUT = 30 * 1000; // 30 seconds for testing
const WARNING_TIME = 10 * 1000; // Show warning 10 seconds before logout

function setupAutoLogout() {
    console.log("⏰ Auto logout system activated");

    let lastActivity = Date.now();
    let warningShown = false;
    let logoutTimer = null;

    // Reset timer on any user activity
    const resetTimer = () => {
        lastActivity = Date.now();
        if (warningShown) {
            console.log("✅ Activity detected - auto logout cancelled");
            warningShown = false;
            // Hide warning if visible
            hideWarning();
        }
    };

    // Add event listeners for all user activities
    const activities = [
        'mousemove', 'mousedown', 'click', 'scroll',
        'keydown', 'keypress', 'keyup',
        'touchstart', 'touchmove', 'touchend',
        'input', 'change', 'focus'
    ];

    activities.forEach(activity => {
        document.addEventListener(activity, resetTimer, { passive: true });
    });

    // Also listen on window
    window.addEventListener('mousemove', resetTimer, { passive: true });
    window.addEventListener('keydown', resetTimer, { passive: true });

    // Show visual warning to user
    function showWarning(secondsLeft) {
        if (warningShown) return;

        warningShown = true;
        console.log(`⚠️ Warning: You will be logged out in ${secondsLeft} seconds`);

        // Create warning element
        const warningDiv = document.createElement('div');
        warningDiv.id = 'auto-logout-warning';
        warningDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #fff3cd;
            border: 2px solid #ffc107;
            color: #856404;
            padding: 15px 20px;
            border-radius: 8px;
            z-index: 10000;
            font-family: Arial, sans-serif;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            max-width: 350px;
            font-size: 14px;
        `;

        warningDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 20px;">⚠️</span>
                <div>
                    <strong>Auto Logout Warning</strong><br>
                    You will be logged out in <span id="logout-countdown">${secondsLeft}</span> seconds due to inactivity.
                    <br><small style="color: #666;">Move your mouse or press any key to cancel.</small>
                </div>
            </div>
        `;

        document.body.appendChild(warningDiv);

        // Update countdown every second
        let countdown = secondsLeft;
        const countdownInterval = setInterval(() => {
            countdown--;
            const countdownElement = document.getElementById('logout-countdown');
            if (countdownElement) {
                countdownElement.textContent = countdown;
            }
            if (countdown <= 0) {
                clearInterval(countdownInterval);
            }
        }, 1000);

        // Auto-remove when logout happens or activity resumes
        return countdownInterval;
    }

    function hideWarning() {
        const warning = document.getElementById('auto-logout-warning');
        if (warning) {
            warning.remove();
        }
    }

    function performLogout() {
        console.log("🔒 Logging out due to inactivity");
        hideWarning();

        // Clear any pending timers
        if (logoutTimer) {
            clearTimeout(logoutTimer);
        }

        // Perform logout
        window.location.href = "/web/session/logout?auto_logout=true";
    }

    // Main check function
    function checkInactivity() {
        const idleTime = Date.now() - lastActivity;
        const remainingTime = IDLE_TIMEOUT - idleTime;

        console.log(`⏰ Idle for ${Math.floor(idleTime/1000)}s / ${IDLE_TIMEOUT/1000}s`);

        // Show warning when remaining time reaches warning threshold
        if (remainingTime <= WARNING_TIME && !warningShown) {
            showWarning(Math.ceil(remainingTime / 1000));
        }

        // Logout when timeout reached
        if (idleTime > IDLE_TIMEOUT) {
            performLogout();
        }
    }

    // Start checking every second
    logoutTimer = setInterval(checkInactivity, 1000);

    // Cleanup function
    return () => {
        if (logoutTimer) {
            clearInterval(logoutTimer);
        }
        hideWarning();
        activities.forEach(activity => {
            document.removeEventListener(activity, resetTimer);
        });
    };
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupAutoLogout);
} else {
    setupAutoLogout();
}

// For Odoo framework compatibility
export default {
    setup: setupAutoLogout
};