
/* =====================================================
   PROOFMIRROR SHIELD — DASHBOARD INTERACTIONS
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("reportSearch");
    const riskFilter = document.getElementById("riskFilter");
    const tableBody = document.getElementById("reportsTableBody");
    const noResults = document.getElementById("noReportsFound");

    if (!tableBody) return;

    const rows = Array.from(
        tableBody.querySelectorAll(".report-row")
    );


    function filterReports() {

        const searchTerm = searchInput
            ? searchInput.value.trim().toLowerCase()
            : "";

        const selectedRisk = riskFilter
            ? riskFilter.value
            : "all";

        let visibleCount = 0;

        rows.forEach(function (row) {

            const rowText = (
                row.dataset.search || row.textContent
            ).toLowerCase();

            const rowRisk = (
                row.dataset.risk || ""
            ).toLowerCase();

            const matchesSearch = rowText.includes(searchTerm);

            const matchesRisk =
                selectedRisk === "all" ||
                rowRisk === selectedRisk;

            const shouldShow = matchesSearch && matchesRisk;

            row.hidden = !shouldShow;

            if (shouldShow) {
                visibleCount++;
            }

        });


        if (noResults) {
            noResults.hidden =
                rows.length === 0 || visibleCount > 0;
        }

    }


    if (searchInput) {
        searchInput.addEventListener("input", filterReports);
    }

    if (riskFilter) {
        riskFilter.addEventListener("change", filterReports);
    }


    // Refresh the dashboard using the current server-rendered data.
    const refreshButton = document.getElementById("refreshDashboard");

    if (refreshButton) {

        refreshButton.addEventListener("click", function () {

            refreshButton.disabled = true;
            refreshButton.textContent = "Refreshing...";

            window.location.reload();

        });

    }


    // Prevent accidental form submission from search controls.
    document.querySelectorAll(".dash-table-tools input").forEach(
        function (input) {
            input.addEventListener("keydown", function (event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                }
            });
        }
    );


    filterReports();

});
