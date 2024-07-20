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
        "/static/themes_client/images/R1.jpg",
        "/static/themes_client/images/R2.jpg",
        "/static/themes_client/images/R3.jpg",
        "/static/themes_client/images/R4.jpg",
      ];
    
      let currentIndex = 0;
    
      function changeBackground() {
        currentIndex = (currentIndex + 1) % images.length;
        $('#slider').css('background-image', `url(${images[currentIndex]})`);
      }
    
      setInterval(changeBackground, 3000); // Change every 3 seconds
  });