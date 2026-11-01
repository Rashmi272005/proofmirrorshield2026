document.addEventListener("DOMContentLoaded", () => {
  const search = document.getElementById("communitySearch");
  const risk = document.getElementById("communityRisk");
  const type = document.getElementById("communityType");
  const rows = [...document.querySelectorAll(".community-row")];
  const empty = document.getElementById("communityNoResults");
  if (!search || !risk || !type) return;
  function filterReports() {
    const term = search.value.trim().toLowerCase();
    let visible = 0;
    rows.forEach(row => {
      const matchesText = (row.dataset.search || "").includes(term);
      const matchesRisk = risk.value === "all" || row.dataset.risk === risk.value;
      const matchesType = type.value === "all" || row.dataset.type === type.value;
      const show = matchesText && matchesRisk && matchesType;
      row.hidden = !show;
      if (show) visible++;
    });
    if (empty) empty.hidden = visible !== 0;
  }
  [search, risk, type].forEach(control => control.addEventListener("input", filterReports));
  [risk, type].forEach(control => control.addEventListener("change", filterReports));
});
