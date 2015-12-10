// every 15 minutes, fetch the home page
// if it is up, refresh (avoids refresh during redeploy)
$(document).ready(function() {
  setInterval(refresh_page, 15*60*1000);
});

function refresh_page() {
  $.get("/", function(data) {
    document.location.reload(true);
  });
};

function register_update(target, url, every, post, pre) {
  var do_update = function () {
    $.ajax(url).done(function(data) {
      if (pre) {
        pre();
      }
      $(target + "-error").html('')
      $(target).html(data);
      if (post) {
        post();
      }
    }).fail(function() {
      $(target + "-error").html('/!\\')
    });
  }

  do_update();
  setInterval(do_update, every*1000);
}
