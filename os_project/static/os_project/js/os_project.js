document.addEventListener("DOMContentLoaded", function () {
  // Get favorite button
  const favoriteBtn = document.querySelector(".favorite-btn");

  if (favoriteBtn) {
    favoriteBtn.addEventListener("click", function (e) {
      e.preventDefault();

      // Get the CSRF token from the cookie
      function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
          const cookies = document.cookie.split(";");
          for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
              cookieValue = decodeURIComponent(
                cookie.substring(name.length + 1)
              );
              break;
            }
          }
        }
        return cookieValue;
      }

      const csrftoken = getCookie("csrftoken");
      const url = this.getAttribute("href");

      // Send AJAX request
      fetch(url, {
        method: "POST",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": csrftoken,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Update button appearance based on favorite status
            if (data.is_favorited) {
              favoriteBtn.classList.add("btn-warning");
              favoriteBtn.classList.remove("btn-outline");
              favoriteBtn.setAttribute("title", "Remove from favorites");
            } else {
              favoriteBtn.classList.remove("btn-warning");
              favoriteBtn.classList.add("btn-outline", "btn-warning");
              favoriteBtn.setAttribute("title", "Add to favorites");
            }

            // Show a toast notification
            const toast = document.createElement("div");
            toast.className = "toast toast-top toast-end";
            toast.innerHTML = `
                      <div class="alert alert-success">
                          <span>${data.message}</span>
                      </div>
                  `;
            document.body.appendChild(toast);

            // Remove the toast after 3 seconds
            setTimeout(() => {
              toast.style.opacity = "0";
              setTimeout(() => {
                toast.remove();
              }, 300);
            }, 3000);
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    });
  }
});
