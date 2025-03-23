document.addEventListener("DOMContentLoaded", function () {
  const toasts = document.querySelectorAll(".toast .alert");

  if (toasts.length > 0) {
    // Add transition styles to all alerts
    toasts.forEach((toast) => {
      toast.style.transition =
        "opacity 0.5s ease-in-out, transform 0.5s ease-in-out";
    });

    // Set timeout to fade out and remove toasts
    setTimeout(function () {
      toasts.forEach((toast, index) => {
        // Stagger the fadeout slightly for multiple toasts
        setTimeout(() => {
          toast.style.opacity = "0";
          toast.style.transform = "translateX(30px)";

          // Remove from DOM after animation completes
          setTimeout(() => {
            toast.remove();
          }, 500);
        }, index * 200);
      });
    }, 3000);
  }
});

//** Funtion to track and store preferred theme */
document.addEventListener("DOMContentLoaded", function () {
  const themeToggle = document.querySelector(".theme-controller");
  const themeKey = themeToggle.getAttribute("data-key") || "theme"; // Defaults to "theme" if no key is set

  // Apply stored theme preference
  const savedTheme = localStorage.getItem(themeKey);
  if (savedTheme) {
    document.documentElement.setAttribute("data-theme", savedTheme);
    themeToggle.checked = savedTheme === "light";
  }

  // Listen for changes
  themeToggle.addEventListener("change", function () {
    const newTheme = themeToggle.checked ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem(themeKey, newTheme);
  });
});
