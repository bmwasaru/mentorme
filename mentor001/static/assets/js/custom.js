////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// jQuery
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
$(document).ready(function($) {
    "use strict";

    $(".nav-toggle").on('click',function (e) {
        $(".main-nav nav").toggleClass("show-nav");
    });

//  Revolution Slider

    if( $(".rev-slider").length ){
        $(".rev-slider").revolution({
            sliderType:"standard",
            sliderLayout:"hero",
            delay:9000,
            gridheight:650,
            navigation: {
                arrows:{enable:true}
            }
        });
    }

//  Calendar

    if( $(".calendar").length ){
        $(".calendar").zabuto_calendar({
            ajax: {
                url: "assets/external/calendar.php",
                modal: true
            },
            action: function () {
                return checkDate(this.id);
            },
            language: "en",
            show_previous: false,
            today: true,
            nav_icon: {
                prev: '<i class="arrow_left"></i>',
                next: '<i class="arrow_right"></i>'
            }
        });
    }

//  Smooth Scroll

    $('.main-nav a[href^="#"], a[href^="#"].scroll').on('click',function (e) {
        e.preventDefault();
        var target = this.hash,
            $target = $(target);
        $('html, body').stop().animate({
            'scrollTop': $target.offset().top
        }, 2000, 'swing', function () {
            window.location.hash = target;
        });
    });

//  Radio buttons in modal

    $(".times .btn").on("click", function() {
        $(this).parent().find("input[type=radio]").attr("checked", false);
        $(this).find("input[type=radio]").attr("checked", true);
    });

//  Owl Carousel

    if( $(".owl-carousel").length ){
        $(".owl-carousel").owlCarousel({
            margin:30,
            items: 4,
            navText: []
        });
    }

//  Fit Videos

    if( $(".video").length ){
        $(".video").fitVids();
    }

//  Form Validation

    $("#form-subscribe button").on("click", function(){
        $("#form-subscribe").validate({
            submitHandler: function() {
                $.post("assets/external/subscribe.php", $("#form-subscribe").serialize(),  function(response) {
                    $('#form-subscribe .form-status').html(response);
                    $('#form-subscribe button').attr('disabled','true');
                });
                return false;
            }
        });
    });

    $("#form-daily-motivation button").on("click", function(){
        $("#form-daily-motivation").validate({
            submitHandler: function() {
                $.post("assets/external/daily_motivation.php", $("#form-daily-motivation").serialize(),  function(response) {
                    $('#form-daily-motivation input').val(response);
                    $('#form-daily-motivation button').attr('disabled','true');
                });
                return false;
            }
        });
    });

    $("#form-contact button").on("click", function(){
        $("#form-contact").validate({
            submitHandler: function() {
                $.post("assets/external/contact.php", $("#form-contact").serialize(),  function(response) {
                    $('#form-contact .form-status').html(response);
                    $('#form-contact button').attr('disabled','true');
                });
                return false;
            }
        });
    });

});

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// On Load
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

$(window).load(function(){
    var $equalHeight = $('.container');
    for( var i=0; i<$equalHeight.length; i++ ){
        equalHeight( $equalHeight );
    }
});

$(window).resize(function(){
    var $equalHeight = $('.container');
    for( var i=0; i<$equalHeight.length; i++ ){
        equalHeight( $equalHeight );
    }
});

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function checkDate(id) {
    var date = $("#" + id).data("date");
    var hasEvent = $("#" + id).data("hasEvent");
    $('#modal').modal();
}

function equalHeight(container){
    var currentTallest = 0,
        currentRowStart = 0,
        rowDivs = new Array(),
        $el,
        topPosition = 0;

    $(container).find('.equal-height').each(function() {
        $el = $(this);
        $($el).height('auto');
        topPostion = $el.position().top;
        if (currentRowStart != topPostion) {
            for (currentDiv = 0 ; currentDiv < rowDivs.length ; currentDiv++) {
                rowDivs[currentDiv].height(currentTallest);
            }
            rowDivs.length = 0; // empty the array
            currentRowStart = topPostion;
            currentTallest = $el.height();
            rowDivs.push($el);
        } else {
            rowDivs.push($el);
            currentTallest = (currentTallest < $el.height()) ? ($el.height()) : (currentTallest);
        }
        for (currentDiv = 0 ; currentDiv < rowDivs.length ; currentDiv++) {
            rowDivs[currentDiv].height(currentTallest);
        }
    });
}