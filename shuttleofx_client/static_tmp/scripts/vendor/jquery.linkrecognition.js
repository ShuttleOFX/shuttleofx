(function ($) {
    $.fn.LinkRecognition = function (options) {
        var defaults = {
            cssClass: '',
            target: '_blank'
        }
        var settings = $.extend({}, defaults, options);
        var selector = $(this);
        var regex = /(https?:\/\/([-\w\.]+)+(:\d+)?(\/([\w\/_\.]*(\?\S+)?)?)?)/ig
        $(selector).html($(selector).html().replace(regex, "<a href='$1' target='" + settings.target + "' class='" + settings.cssClass + "'>$1</a>"));
    }
})(jQuery);