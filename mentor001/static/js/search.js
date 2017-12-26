$(function() {
    $(".questions-results li").click(function () {
        var question = $(this).attr("question-id");
        location.href = "/questions/" + question + "/";
    });
});