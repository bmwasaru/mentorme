// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// $("#id_username").change(function () {
//       var username = $(this).val();

//       $.ajax({
//         url: '/accounts/ajax/validate_username/',
//         data: {
//           'username': username
//         },
//         dataType: 'json',
//         success: function (data) {
//           if (data.is_taken) {
//             alert("A user with this username already exists.");
//           }
//         }
//       });

//     });