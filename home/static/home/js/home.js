  function updateImageSrc() {
    const img = document.getElementById('theme-image');
    const isLightTheme = document.documentElement.getAttribute('data-theme') === 'light';
    img.src = isLightTheme
      ? 'https://res.cloudinary.com/dj2lk9daf/image/upload/v1742737056/ada-badass-light-theme-black-glasses.png_jiijhx.png'
      : 'https://res.cloudinary.com/dj2lk9daf/image/upload/v1742737056/ada-badass-dark-theme-purple-glasses.png_zpunfu.png';
  }
  // Run on page load
  updateImageSrc();
  // Listen for theme changes (if theme changes dynamically)
  const observer = new MutationObserver(updateImageSrc);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
