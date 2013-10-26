(function ($) {
  "use strict";

  var urlParam = function(name){
    var results = new RegExp('[\\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results)
      return results[1] || 0;
    return null;
  }

  var target = 'suggest-drink';
  var targetDiv = $('#' + target);

  var getDrink = function() {
    var spinner
      , spinnerOpts = {
          lines: 13, // The number of lines to draw
          length: 20, // The length of each line
          width: 10, // The line thickness
          radius: 30, // The radius of the inner circle
          corners: 1, // Corner roundness (0..1)
          rotate: 0, // The rotation offset
          direction: 1, // 1: clockwise, -1: counterclockwise
          color: '#000', // #rgb or #rrggbb or array of colors
          speed: 1, // Rounds per second
          trail: 60, // Afterglow percentage
          shadow: false, // Whether to render a shadow
          hwaccel: false, // Whether to use hardware acceleration
          className: 'spinner', // The CSS class to assign to the spinner
          zIndex: 2e9, // The z-index (defaults to 2000000000)
          top: 'auto', // Top position relative to parent in px
          left: 'auto' // Left position relative to parent in px
        };

    targetDiv.empty();
    spinner = new Spinner(spinnerOpts).spin(document.getElementById(target));

    if (urlParam('lat') && urlParam('lon')) {
      getDrinkForPosition({coords: {latitude: urlParam('lat'), longitude: urlParam('lon')}});
    }
    else if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(getDrinkForPosition, positionError);
    }
    else {
      $('#' + target).text("Sorry, no location access :(");
    }
  };

  var getDrinkForPosition = function(position) {
    console.log(position.coords.latitude + " " + position.coords.longitude);


    $.get("gimme_drink/"+position.coords.latitude+"/"+position.coords.longitude)
      .done(function (data) {
        var showDrink = function(drink_index) {
          drink_index = drink_index % data.cocktails.length;
          console.log("DRINK", data.cocktails[drink_index]);
          targetDiv.html(
            _.template($('#drink-template').html(), data.cocktails[drink_index])
          );

          $('#another-drink')
            .on('click', function() { showDrink(drink_index+1); })
            .on('mouseover', function() {
              var glass = $("#glass");
              if (!glass.hasClass("shake")) {
                glass.addClass("shake");
              } else {
                glass.css('animation-name', 'none');
                glass.css('-moz-animation-name', 'none');
                glass.css('-webkit-animation-name', 'none');

                setTimeout(function() {
                  glass.css('-webkit-animation-name', 'shake');
                }, 0);
              }
            });
        };

        showDrink(0);
      })
      .fail(function() {
        targetDiv.html("Something went terribly wrong :(");
      });

  };

  var positionError = function(err) {
    if (err.code == 1) {
      $('#' + target).text("Access to position data denied :( Please enable it!");
    } else if (err.code == 2) {
      $('#' + target).text("Your position is not available :(");
    }
  };

  $(function () {
    getDrink();

    $(document).keydown(function(e) {
      if (e.keyCode == 13 || e.keyCode == 39) {
        $("#another-drink").click();
      }
    });
  });
})(jQuery);
