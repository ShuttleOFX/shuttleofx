
Dropzone.autoDiscover = false;
var bundleId = undefined;
var myDropzone = undefined;

$("#droparea").hide();
$('#fileSubmit').hide();
$('#upload_feeback').hide();


$(function(){
    var wofxDropzone = new Dropzone("#droparea", {
        url: "undefinedUrl",
        acceptedFiles: "application/zip, application/x-tar, application/gzip, application/x-gzip",
        maxFilesize: 1024,
        paramName: "file",
    });

    wofxDropzone.options.previewTemplate = '\
        <div class="dz-preview dz-file-preview">\
            <div class="dz-details">\
                <div class="dz-filename"><span data-dz-name></span></div>\
                <div class="dz-size" data-dz-size></div>\
                <img data-dz-thumbnail />\
            </div>\
        <div class="dz-progress"><span class="dz-upload" data-dz-uploadprogress></span></div>\
        <div class="dz-error-message"><span data-dz-errormessage></span></div>\
        </div>';

    $('#fileSubmit').click(function(){
        console.log(wofxDropzone.getQueuedFiles().length)
        if (wofxDropzone.getQueuedFiles().length > 0) {
            wofxDropzone.processQueue();
        }else{
            $('#message').html('You have forgotten to attach your file !')
            $('#upload_feedback').show();
        }
    });

    $('#metaBundle').submit(function(event, bundleId){
        event.preventDefault();

        $('#upload_feedback').hide();

        bundleName = $("#bundleName").val();
        bundleDescription = $("#bundleDescription").val();
        var userId = $("#createBundle").attr("attr-id");

        $.ajax({
            type : 'POST',
            url : '/bundle',
            data : {'bundleName' : bundleName, 'bundleDescription' : bundleDescription, 'userId' : userId}
        }).done(function(data, bundleId){
            
            $("#droparea").show();
            $('#fileSubmit').show();
            $("#createBundle").hide();

            bundleId = data.bundleId;
            var bundleURI = "/bundle/"+bundleId+"/archive";
            wofxDropzone.options.url = bundleURI;
            //console.log("bundleId "+bundleId);

            wofxDropzone.on('success', function(){
                var bundleAnalyseURI = '/bundle/'+bundleId+'/analyse';
                $.ajax({
                    type : 'POST',
                    url : bundleAnalyseURI,
                    data : {"bundleId" : bundleId},
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        console.log("Status: " + textStatus + "Error: " + errorThrown); 

                        $("h2").html("Oops... something went wrong !")
                        $("#metaBundle").hide();
                        $("#droparea").hide();
                        $('#fileSubmit').hide();
                        $("#createBundle").hide();
                        $('#message').html('Your bundle is invalid.')
                        $('#upload_feedback').show();
                    }
                }).done(function(){
                    console.log("upload done.");
                    $("h2").html("Congratulations !")
                    $("#metaBundle").hide();
                    $("#droparea").hide();
                    $('#fileSubmit').hide();
                    $("#createBundle").hide();
                    $('#message').html('Your bundle has been successfully uploaded ! <i class="fa fa-rocket"></i>')
                    $('#upload_feedback').show();
                })
            });
        });
    });
});


