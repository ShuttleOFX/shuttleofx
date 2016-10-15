$(document).ready(function () {

    // Display an example image in full size
    function changeFullSizeDisplay (pluginId, imageId) {
        $("#fullSizeDisplay").attr("src", "/plugin/" + pluginId + "/image/" + imageId);
    }

    $(".gallery-preview-img").click(function(event) {

        var pluginId = $(this).parent().find("img").attr("src").split("/plugin/")[1].split("/thumbnail/")[0];
        var imageId = $(this).parent().find("img").attr("src").split("/thumbnail/")[1];

        changeFullSizeDisplay(pluginId, imageId);
    });


    // Set an example image as the default image for the plugin
    function setDefaultImage (pluginId, imageId) {

        $.ajax({
                type: "POST",
                url: "/plugin/" + pluginId + "/defaultImage/" + imageId,
                async: false //avoid an empty data when result is returned.
            }).done(function(){
                $(".set-default-img").removeClass("disabled").find('i').attr("class", "fa fa-star");
            })
    }

    $(".set-default-img").click(function(event) {

        var pluginId = $(this).parent().find("img").attr("src").split("/plugin/")[1].split("/thumbnail/")[0];
        var imageId = $(this).parent().find("img").attr("src").split("/thumbnail/")[1];

        setDefaultImage(pluginId, imageId);
        $(this).addClass("disabled").find('i').attr("class", "fa fa-check");
    });

// recognize URLs and make them cliquable

    if ($(".plugin-description").length) {
        $(".plugin-description").LinkRecognition({
            target: "_blank",
            cssClass: "external-link"
        });
    }
    
    console.log($(".comment-content"))
    if ($(".comment-content").length) {
        $(".comment-content").each(function(){
            $(this).LinkRecognition({
                target: "_blank",
                cssClass: "external-link"
            });
        })
     }
});
