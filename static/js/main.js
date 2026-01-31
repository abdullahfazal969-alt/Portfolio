// This is the main JavaScript file for your portfolio.
// We will add animations and interactive features here.

document.addEventListener("DOMContentLoaded", (event) => {
    console.log("Portfolio site is loaded and ready for animations!");

    // Example: Add a class to a project card on hover
    const projectCards = document.querySelectorAll(".project-card");
    projectCards.forEach((card) => {
        card.addEventListener("mouseenter", () => {
            card.classList.add("hovered");
        });
        card.addEventListener("mouseleave", () => {
            card.classList.remove("hovered");
        });
    });
});
// ===== Footer Local Time Updater =====
(function updateLocalTime() {
    function pad(n) {
        return (n < 10 ? "0" : "") + n;
    }

    function showTime() {
        const el = document.getElementById("local-time");
        if (!el) return;

        const now = new Date();
        const hours = now.getHours();
        const minutes = pad(now.getMinutes());
        const isPM = hours >= 12;
        const hour12 = ((hours + 11) % 12) + 1;

        let tz = "LOCAL";
        try {
            const tzFull =
                Intl.DateTimeFormat().resolvedOptions().timeZone || "";
            tz = tzFull.split("/").pop().replace("_", " ") || "LOCAL";
        } catch (e) {}

        el.textContent = `${pad(hour12)}:${minutes} ${isPM ? "PM" : "AM"} ${tz}`;
    }

    showTime();
    setInterval(showTime, 60000);
})();
