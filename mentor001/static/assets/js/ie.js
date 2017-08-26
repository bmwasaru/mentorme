$(document).ready(function($) {

    "use strict";

    $(".animate").animate({ opacity: 0 });
    $(".caption-text").animate({ opacity: 0 });

    Pace.on('done', function() {
        $(".overlay").animate({ opacity: 0 }, 2000);
        $(".animate").animate({ opacity: 1 }, 1000);

    });

    $(".navigation-items li").animate({ opacity: 0 });
    $(".block-wrapper").animate({ opacity: 0 });
    $(".block-wrapper").animate({ marginTop: "20px" });
    $('.block-wrapper').appear();
    $('.block-wrapper').on('appear', function() {
        $(this).animate({
            opacity: 1
        }, { duration: 800, queue: false });

        $(this).animate({ marginTop: "0px" });
        $(this).addClass("show");
        if( !$(".numbers").hasClass("counting") && !$(".numbers").hasClass("count-down") ){
            initializeCounterUp();
            $(".numbers").addClass("counting");
        }
    });


    $(".navigation-button").on("click", function() {
        if( $("body").hasClass("show-nav") ){
            $(".overlay").animate({ opacity: 1 }, 1000);
            $(".animate").animate({
                opacity: 0
            }, { duration: 1000, queue: false });
            $(".main-navigation").animate({
                opacity: 1
            }, { duration: 1000, queue: false });

            $.each( $(".navigation-items li"), function (i) {
                var $this = $(this);
                setTimeout(function(){
                    $this.animate({ opacity: 1 });
                }, i * 100);
            });

        }
        else {
            $(".overlay").animate({ opacity: 0 }, 1000);
            $(".animate").animate({ opacity: 1 });
            $(".navigation-items li").animate({ opacity: 0 });
        }
    });

    $(".navigation-items a").on("click", function() {
        $(".overlay").animate({ opacity: 0 }, 1000);
        $(".animate").animate({ opacity: 1 });
        $(".navigation-items li").animate({ opacity: 0 });
    });

    $(".overlay").on("click", function() {
        $(".overlay").animate({ opacity: 0 }, 1000);
        $(".animate").animate({ opacity: 1 });
        $(".navigation-items li").animate({ opacity: 0 });
    });

});