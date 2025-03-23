document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.getElementById("favorites-sidebar");
  const toggleBtn = document.getElementById("toggle-button");

  let isLockedOpen = false;

  // Click to lock/unlock
  sidebar.addEventListener("click", function (e) {
    // Avoid closing if clicking a link
    if (e.target.tagName.toLowerCase() === "a") {
      return;
    }

    isLockedOpen = !isLockedOpen;
    if (isLockedOpen) {
      sidebar.classList.add("open");
      sidebar.classList.remove("closed");
    } else {
      sidebar.classList.remove("open");
      sidebar.classList.add("closed");
    }
  });

  // Click outside to close
  document.addEventListener("click", function (e) {
    const clickedInsideSidebar = sidebar.contains(e.target);
    const clickedToggleButton = toggleBtn.contains(e.target);

    if (
      sidebar.classList.contains("open") &&
      !clickedInsideSidebar &&
      !clickedToggleButton
    ) {
      sidebar.classList.remove("open");
      sidebar.classList.add("closed");
      isLockedOpen = false;
    }
  });
});
