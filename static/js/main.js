document.addEventListener("DOMContentLoaded", function () {

    // Highlight the current navigation link
    const currentPath = window.location.pathname;

    document.querySelectorAll(".nav-links a").forEach(function (link) {
        const linkPath = new URL(link.href).pathname;

        if (linkPath === currentPath) {
            link.classList.add("active");
            link.setAttribute("aria-current", "page");
        }
    });

    // Update footer year automatically
    document.querySelectorAll("[data-current-year]").forEach(function (element) {
        element.textContent = new Date().getFullYear();
    });

    // Prevent accidental repeated form submissions
    document.querySelectorAll("form[data-prevent-double-submit]").forEach(function (form) {
        form.addEventListener("submit", function () {
            const submitButton = form.querySelector('[type="submit"]');

            if (submitButton) {
                submitButton.disabled = true;
            }
        });
    });

});