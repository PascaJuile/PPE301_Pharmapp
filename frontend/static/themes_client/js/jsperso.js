$(document).ready(function() {
    // Au survol, changer la couleur du texte
    $('.site-navigation .site-menu li a').hover(
      function() {
        $(this).css('color', '#fff');
      },
      function() {
        $(this).css('color', '#000');
      }
    );
    const images = [
      "/static/themes_client/images/Back.jpg",
      "/static/themes_client/images/Back1.jpg",
      "/static/themes_client/images/Back2.jpg",
      "/static/themes_client/images/Back3.jpg",
      "/static/themes_client/images/Back4.jpg",
  ];

  let currentIndex = 0;

  function changeBackground() {
      currentIndex = (currentIndex + 1) % images.length;
      $('#slider').css('background-image', `url(${images[currentIndex]})`);
  }

  $(document).ready(function() {
      // Set the initial background image
      $('#slider').css('background-image', `url(${images[currentIndex]})`);
      // Change the background image every 3 seconds
      setInterval(changeBackground, 3000);
    });
  });