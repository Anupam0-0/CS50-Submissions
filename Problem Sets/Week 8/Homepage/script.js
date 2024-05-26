function goToDefault() {
    console.log("Button clicked"); // Debug message
    window.location.href = "xdefault.html";
}

let afkTimeout;

function resetAfkTimeout() {
    clearTimeout(afkTimeout);
    afkTimeout = setTimeout(() => {
        alert("You have been inactive for 15 seconds.");
    }, 15000); // 15 seconds
}

// Add event listeners for various user activities
function setupActivityListeners() {
    window.addEventListener('mousemove', resetAfkTimeout);
    window.addEventListener('keydown', resetAfkTimeout);
    window.addEventListener('scroll', resetAfkTimeout);
    window.addEventListener('click', resetAfkTimeout);
}

// Initialize the AFK timeout and activity listeners when the page loads
window.onload = function() {
    setupActivityListeners();
    resetAfkTimeout();      // Start the initial timeout
};
