(function ($) {
  "use strict";

  var urlParam = function(name) {
    var results = new RegExp('[\\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results)
      return results[1] || 0;
    return null;
  };

  var target = 'suggest-drink';
  var targetDiv = $('#' + target);
  var spinnerOpts = {
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

  var getDrink = function() {
    var spinner
    targetDiv.empty();
    spinner = new Spinner(spinnerOpts).spin(document.getElementById(target));

    if (urlParam('lat') && urlParam('lon')) {
      getDrinkForPosition({coords: {latitude: urlParam('lat'), longitude: urlParam('lon')}});
    }
    else if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(getDrinkForPosition, positionError);
    }
    else {
      getDrinkForPosition({coords: {latitude: 0, longitude: 0}});
    }
  };

  var getDrinkForPosition = function(position) {
    var req_string;

    if (position.zmw)
      req_string = position.zmw;
    else
      req_string = position.coords.latitude+"/"+position.coords.longitude;

    $.get("gimme_drink/"+req_string)
      .done(function (data) {
        var showDrink = function(drink_index) {
          drink_index = drink_index % data.cocktails.length;
          targetDiv.html(
            _.template(
              $('#drink-template').html(),
              $.extend(data.cocktails[drink_index], {sentence: data.sentence})
            )
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

          $('#thumbs-up').on('click', function() {
            var $this = $(this);
            $.post('/pump_it_up/' + $this.data('drink-id'), function() {
              $this.addClass("btn-primary disabled");
              $this.find("span").text("Voted");
            });
          });
        };

        $('#more-info').css('visibility', 'visible');
        data.city = data.city || "Unknown";
        data.weather = data.weather || "N.A.";
        data.temperature = data.temperature || "N.A.";

        $('#location-info')
          .css('visibility', 'visible')
          .find('input').val(data.city);
        $('#weather-info').text(data.weather);
        $('#temperature-info').text(data.temperature);

        window.history.pushState(
          null, null,
          window.location.href.split("?")[0] + "?lat=" + data.lat + "&lon=" + data.lon
        );

        showDrink(0);
      })
      .fail(function() {
        targetDiv.html("Something went terribly wrong :(");
      });

  };

  var positionError = function() {
    getDrinkForPosition({coords: {latitude: 0, longitude: 0}});
  };

  $(function () {
    getDrink();

    $('#location-info').css('visibility', 'hidden');

    $(".city-selector").autocomplete({
      source: function(request, response) {
        $.ajax({
          url: "http://autocomplete.wunderground.com/aq?cb=?",
          dataType: "jsonp",
          data: {
            query: request.term
          },
          success: function(data) {
            response($.map(data.RESULTS, function(item) {
              return {
                label: item.name,
                value: item.name,
                zmw: item.zmw
              }
            }));
          }
        });
      },
      minLength: 3,
      select: function(event, ui) {
        var spinner;
        targetDiv.empty();
        $('#more-info').css('visibility', 'hidden');
        spinner = new Spinner(spinnerOpts).spin(document.getElementById(target));
        getDrinkForPosition({zmw: ui.item.zmw});
      }
    });

    $(document).keydown(function(e) {
      if (e.keyCode == 13) {
        $("#another-drink").click();
      }
    });
  });
})(jQuery);
