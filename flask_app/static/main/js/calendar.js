document.addEventListener("DOMContentLoaded", () => {
  const calendarEl = document.getElementById("calendarGrid");
  const selectedDates = new Set();
  const hiddenInput = document.getElementById("specific_dates");

  const today = new Date();

  for (let i = 0; i < 42; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() + i);
    const dateStr = date.toISOString().split("T")[0];

    // Create date cell
    const cell = document.createElement("div");
    cell.className = "calendar-cell";
    cell.textContent = dateStr.slice(5);
    cell.dataset.date = dateStr;

    // Toggle selection
    cell.addEventListener("click", () => {
      if (selectedDates.has(dateStr)) {
        selectedDates.delete(dateStr);
        cell.classList.remove("selected");
      } else {
        selectedDates.add(dateStr);
        cell.classList.add("selected");
      }

      // Update hidden input
      hiddenInput.value = Array.from(selectedDates).sort().join(",");
    });

    calendarEl.appendChild(cell);
  }
});
