document.addEventListener("DOMContentLoaded", function () {

    const messageInput = document.getElementById("message");
    const urlInput = document.getElementById("url");

    // Find the form containing the verification inputs
    const form = messageInput
        ? messageInput.closest("form")
        : null;

    if (!form || (!messageInput && !urlInput)) {
        return;
    }

    const submitButton = form.querySelector('[type="submit"]');

    // Create an error message area safely
    let errorBox = document.getElementById("verificationError");

    if (!errorBox) {
        errorBox = document.createElement("div");
        errorBox.id = "verificationError";
        errorBox.setAttribute("role", "alert");
        errorBox.style.color = "#ff8585";
        errorBox.style.marginTop = "12px";
        errorBox.style.fontSize = "13px";

        form.appendChild(errorBox);
    }

    form.addEventListener("submit", async function (event) {

        event.preventDefault();

        errorBox.textContent = "";

        const text = messageInput ? messageInput.value.trim() : "";
        const url = urlInput ? urlInput.value.trim() : "";

        // Validate input
        if (!text && !url) {
            errorBox.textContent =
                "Please enter a message or URL to verify.";
            return;
        }

        if (text.length > 10000) {
            errorBox.textContent =
                "Message is too long. Maximum 10,000 characters allowed.";
            return;
        }

        if (url.length > 2048) {
            errorBox.textContent =
                "URL is too long. Maximum 2,048 characters allowed.";
            return;
        }

        // Loading state
        const originalButtonText = submitButton
            ? submitButton.textContent
            : "";

        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = "Analyzing...";
        }

        try {

            const response = await fetch("/api/analyze", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text: text,
                    url: url
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || data.message ||
                    "Verification failed. Please try again."
                );
            }

            // Redirect to the generated result page
            if (data.result_url) {
                window.location.href = data.result_url;
                return;
            }

            // Fallback if backend returns a report ID
            if (data.report_id !== undefined) {
                window.location.href = "/result/" +
                    encodeURIComponent(data.report_id);
                return;
            }

            throw new Error(
                "Analysis completed, but the backend did not return a result URL."
            );

        } catch (error) {

            errorBox.textContent =
                error.message || "Something went wrong.";

            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = originalButtonText;
            }

        }

    });

    // Character counter, if present in the page
    if (messageInput) {

        const counter = document.getElementById("charCount");

        function updateCounter() {
            if (counter) {
                counter.textContent =
                    messageInput.value.length + " / 10000";
            }
        }

        messageInput.addEventListener("input", updateCounter);

        updateCounter();
    }

});