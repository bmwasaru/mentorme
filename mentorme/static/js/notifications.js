$(function () {
  var bell = $('#notifications');
  if (!bell.length) return;
  var badge = $('#notification-count');
  var timer;
  var checking = false;

  function updateCount(count) {
    bell.toggleClass('new-notifications', count > 0);
    bell.attr('aria-label', 'Notifications, ' + count + ' unread');
    badge.text(count).toggle(count > 0);
  }

  function scheduleCheck() {
    window.clearTimeout(timer);
    if (!document.hidden) timer = window.setTimeout(checkNotifications, 30000);
  }

  function checkNotifications() {
    if (document.hidden || checking) return;
    checking = true;
    $.ajax({
      url: bell.data('count-url'),
      cache: false,
      success: function (data) {
        var count = Number(data);
        if (Number.isFinite(count)) updateCount(count);
      },
      complete: function () {
        checking = false;
        scheduleCheck();
      }
    });
  }

  bell.popover({html: true, content: 'Loading...', trigger: 'manual'});
  bell.on('click', function (event) {
    event.preventDefault();
    if (bell.attr('aria-expanded') === 'true') {
      bell.popover('hide').attr('aria-expanded', 'false');
      return;
    }
    bell.popover('show').attr('aria-expanded', 'true');
    $('.popover-content').text('Loading notifications…');
    $.ajax({
      url: bell.data('preview-url'),
      cache: false,
      success: function (data) { $('.popover-content').html(data); },
      error: function () { $('.popover-content').text('Could not load notifications. Please try again.'); }
    });
  });

  document.addEventListener('visibilitychange', function () {
    window.clearTimeout(timer);
    if (!document.hidden) checkNotifications();
  });
  checkNotifications();
});
