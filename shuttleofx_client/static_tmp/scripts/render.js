$(document).ready(function () {

    var tmp;

    $('#'.selectedResource).addClass('selected');

    function formToJson() {
        var renderParameters = [];
        $("input", $('#renderForm')).each(function (index) {
            var jsonForm = {};
            switch ($(this).attr("ofxType")) {
                case 'OfxParamTypeInteger':
                    jsonForm["id"] = $(this).attr("id");
                    jsonForm["value"] = parseInt(this.value);
                    renderParameters.push(jsonForm);
                    break;
                case 'OfxParamTypeInteger2D':
                    var tab = [];
                    tab.push(parseInt(this.value));
                    tab.push(parseInt(this.value)); // TODO: retrieve the right value
                    jsonForm["id"] = $(this).attr("id");
                    jsonForm["value"] = tab;
                    renderParameters.push(jsonForm);
                    break;
                case 'OfxParamTypeInteger3D':
                    var tab = [];
                    tab.push(parseInt(this.value));
                    tab.push(parseInt(this.value)); // TODO: retrieve the right value
                    tab.push(parseInt(this.value));
                    jsonForm["id"] = $(this).attr("id");
                    jsonForm["value"] = tab;
                    renderParameters.push(jsonForm);
                    break;
                case 'OfxParamTypeRange':
                    jsonForm["id"] = $(this).attr("id");
                    jsonForm["value"] = parseInt(this.value);
                    renderParameters.push(jsonForm);
                    break;
                case 'OfxParamTypeText':
                    jsonForm["id"] = $(this).attr("id");
                    jsonForm["value"] = this.value;
                    renderParameters.push(jsonForm);
                    break;
                case 'OfxParamTypeDouble':
                    jsonForm["id"] = $(this).attr("id");
                    jsonForm["value"] = parseFloat(this.value);
                    renderParameters.push(jsonForm);
                    break;
                case 'OfxParamTypeDouble2D':
                    var tab = [];
                    tab.push(parseFloat(this.value));
                    tab.push(parseFloat(this.value)); // TODO: retrieve the right value
                    jsonForm["id"] = $(this).attr("id");
                    jsonForm["value"] = tab;
                    renderParameters.push(jsonForm);
                    break;
                case 'OfxParamTypeDouble3D':
                    var tab = [];
                    tab.push(parseFloat(this.value));
                    tab.push(parseFloat(this.value)); // TODO: retrieve the right value
                    tab.push(parseFloat(this.value));
                    jsonForm["id"] = $(this).attr("id");
                    jsonForm["value"] = tab;
                    renderParameters.push(jsonForm);
                    break;
                case 'OfxParamTypeString':
                    jsonForm["id"] = $(this).attr("id");
                    jsonForm["value"] = this.value;
                    renderParameters.push(jsonForm);
                    break;
                case 'OfxParamTypeBoolean':
                    if (this.checked) {
                        jsonForm["id"] = $(this).attr("id");
                        jsonForm["value"] = true;
                        renderParameters.push(jsonForm);
                    } else {
                        jsonForm["id"] = $(this).attr("id");
                        jsonForm["value"] = false;
                        renderParameters.push(jsonForm);
                    }
                    break;
                default:
                    jsonForm["id"] = $(this).attr("id");
                    jsonForm["value"] = this.value;
                    renderParameters.push(jsonForm);
                    break;
            }
        });

        $("select", $('#renderForm')).each(function (index) {
            var jsonForm = {};
            jsonForm["id"] = $(this).attr("id");
            jsonForm["value"] = this.value;
            renderParameters.push(jsonForm);
        });

        return renderParameters;
    }

    function renderGenerator(pluginId) {
        displayRenderLoader();
        var renderParameters = formToJson();

        $("#download-view").addClass('disabled');
        $("#addGalleryImage").addClass('disabled');
        $("#render").addClass('disabled');

        $.ajax({
                type: "POST",
                url: "/render",
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify({
                    nodes: [{
                        id: 0,
                        plugin: pluginId,
                        parameters: renderParameters
                    }, {
                        id: 1,
                        plugin: "tuttle.pngwriter",
                        parameters: [{
                            id: "filename",
                            value: "{UNIQUE_OUTPUT_FILE}.png"
                        }]
                    }],
                    connections: [{
                        src: {id: 0},
                        dst: {id: 1}
                    }],
                    options: [],
                }),
            })
            .done(function (data) {
                $("#viewer img#renderedPic").attr("src", "/render/" + data.render.id + "/resource/" + data.render.outputFilename);
                $("#download-view").removeClass('disabled');
                $("#addGalleryImage").removeClass('disabled');
                $("#render").removeClass('disabled');
                hideRenderLoader();
                $('.display img').css({height: "auto"});

                $("#downloadtrigger").off("click").click(function (data) {
                    $("#download-view").addClass('disabled');
                    $("#render").addClass('disabled');
                    $("#addGalleryImage").addClass('disabled');
                    $("#downloadModal").modal('hide');
                    displayDownloadLoader();

                    // Find the appropriate extension for the file to be generated
                    var extension = '.' + $('input[name=format]:checked', '#formatSelect').val();

                    $.ajax({
                            type: "POST",
                            url: "/render",
                            contentType: 'application/json; charset=utf-8',
                            data: JSON.stringify({
                                nodes: [{
                                    id: 0,
                                    plugin: pluginId,
                                    parameters: renderParameters
                                }, {
                                    id: 1,
                                    parameters: [{
                                        id: "filename",
                                        value: "{UNIQUE_OUTPUT_FILE}" + extension
                                    }]
                                }],
                                connections: [{
                                    src: {id: 0},
                                    dst: {id: 1}
                                }],
                                options: [],
                            }),
                        })
                        .done(function (data) {
                            var link = document.createElement("a");
                            link.style.display = "none";
                            link.download = name;
                            link.href = "/render/" + data.render.id + "/resource/" + data.render.outputFilename;
                            document.body.appendChild(link);
                            link.click();
                            link.parentNode.removeChild(link);

                            hideDownloadLoader();
                            $("#download-view").removeClass('disabled');
                            $("#addGalleryImage").removeClass('disabled');
                            $("#render").removeClass('disabled');
                        });
                });
            })
            .error(function (data) {
                console.log('POST ERROR !');
            });
    }

    function renderFilter(pluginId) {
        displayRenderLoader();
        var renderParameters = formToJson();

        $("#download-view").addClass('disabled');
        $("#addGalleryImage").addClass('disabled');
        $("#render").addClass('disabled');

        $.ajax({
            type: "POST",
            url: "/render",
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify({
                nodes: [{
                    id: 0,
                    parameters: [
                        {
                            "id" : "filename",
                            "value" : "{RESOURCES_DIR}/"+ selectedResource
                        },
                        {
                            "id" : "channel",
                            "value" : "rgba"
                        },
                        {
                            "id" : "bitDepth",
                            "value" : "32f"
                        }
                    ]
                },{
                    id: 1,
                    plugin: pluginId,
                    parameters: renderParameters
                },{
                    id: 2,
                    plugin: "tuttle.pngwriter",
                    parameters: [{
                        id: "filename",
                        value:  "{UNIQUE_OUTPUT_FILE}.png"
                    }]
                }],

                connections: [{
                    src: {id: 0},
                    dst: {id: 1}
                },{
                    src: {id: 1},
                    dst: {id: 2}
                }],
                options:[],
            }),
        })
            .done(function (data) {
                removeMessage();

                // Change the extension of the proxy file path to .png
                // Since the displayed proxy is always a generated PNG and not of the type of the original ressource
                // We want to make sure the proxy is sent with the proper extension
                var selectedResourceName = selectedResource.split(".")[0];
                var ext = selectedResource.split(".")[1];
                if (selectedResourceName.indexOf("tmp") <= -1) {
                    var selectedResourcePath = "/proxy/" + selectedResourceName ;
                    ext = ".png";
                }
                else {
                    var selectedResourcePath = "/resource/" + selectedResourceName;
                    ext = "."+ext;
                }
                $("#viewer img#renderedPic").attr("src", "/render/" + data.render.id + "/resource/" + data.render.outputFilename);
                $("#viewer img#originalPic").attr("src", selectedResourcePath + ext);
                $("#viewer img#originalPic").css("width", $("#viewer img#renderedPic").width());
                offset = $("#viewer img#renderedPic").offset;
                $("#viewer img#originalPic").offset({ top: offset.top, left: offset.left});
                $("#viewer img#originalPic").show();
                $("#download-view").removeClass('disabled');
                $("#addGalleryImage").removeClass('disabled');
                $("#render").removeClass('disabled');
                hideRenderLoader();
                $('.display img').css({height: "auto"});
                init_beforeAfterSlider();

                $("#downloadtrigger").off("click").click(function (data) {
                    $("#download-view").addClass('disabled');
                    $("#addGalleryImage").addClass('disabled');
                    $("#render").addClass('disabled');
                    $("#downloadModal").modal('hide');
                    displayDownloadLoader();

                    // Find the appropriate extension for the file to be generated
                    var extension = '.png'
                    if($('input[value=original]', '#formatSelect').is(":checked")) {
                        extension = '.' + selectedResource.split(".")[1];
                    }
                    else {
                        extension = '.' + $('input[name=format]:checked', '#formatSelect').val();
                    }

                    $.ajax({
                            type: "POST",
                            url: "/render",
                            contentType: 'application/json; charset=utf-8',
                            data: JSON.stringify({
                                nodes: [{
                                    id: 0,
                                    parameters: [
                                        {
                                            "id": "filename",
                                            "value": "{RESOURCES_DIR}/" + selectedResource
                                        }
                                    ]
                                }, {
                                    id: 1,
                                    plugin: pluginId,
                                    parameters: renderParameters
                                }, {
                                    id: 2,
                                    parameters: [{
                                        id: "filename",
                                        value: "{UNIQUE_OUTPUT_FILE}" + extension
                                    }]
                                }],

                                connections: [{
                                    src: {id: 0},
                                    dst: {id: 1}
                                }, {
                                    src: {id: 1},
                                    dst: {id: 2}
                                }],
                                options: []
                            })
                        })
                        .done(function (data) {
                            var link = document.createElement("a");
                            link.style.display = "none";
                            link.download = name;
                            link.href = "/render/" + data.render.id + "/resource/" + data.render.outputFilename;
                            document.body.appendChild(link);
                            link.click();
                            link.parentNode.removeChild(link);

                            hideDownloadLoader();
                            $("#download-view").removeClass('disabled');
                            $("#addGalleryImage").removeClass('disabled');
                            $("#render").removeClass('disabled');
                        });
                });
            })
            .error(function (data) {
                console.log('POST ERROR !');
            })
        .error(function(data){
            console.log('POST ERROR !');
            hideRenderLoader();
        });
    }

    // download an image from an url and apply a filter
    function fromUrlRender(pluginId) {
      displayRenderLoader();
      var renderParameters = formToJson();

      $.ajax({
        type: "POST",
        url: "/downloadImgFromUrl",
        contentType: 'application/json; charset=utf-8',
        data : JSON.stringify({
          'url': $("#imgUrl").val()
        }),
          statusCode: {
            500: function() {
              alert( "page not found" );
            }
          }
      })
      .error(function(data) {
            hideRenderLoader();
            $("#imgUrl").parent().before(addMessage(data.responseText, "error"));
      })
      .success(function(data){
          removeMessage();
          selectedResource = data;

          renderFilter(pluginId);
      });
    }

    var allResources = undefined;
    var selectedResource = undefined;

    $.ajax({
            type: "GET",
            url: "/resource",
            async: false, //avoid an empty data when result is returned.
        })
        .done(function (data) {
            allResources = [];

            $.each(data.resources, function (index, resource) {
                allResources.push(resource['registeredName']);
            });

            if (allResources !== undefined && allResources.length > 0) {
                selectedResource = allResources[0];
            }
        })
        .error(function (data) {
            console.log('POST ERROR !');
        });

    $(".sampleImage").each(function () {
        $(this).click(function () {
            $("#imgUrl").parent().css("border-left", "none").css("color", "inherit");
            setResourceSelected($(this));
            var pluginId = $("#render.OfxImageEffectContextFilter").attr("pluginId");
            renderFilter(pluginId);
        });
    });

    function setResourceSelected(obj) {
        $(".sampleImage").each(function () {
            deselect($(this));
        });
        $(obj).parent().css("border-left", "solid 10px rgb(0,150,136)");
        selectedResource = $(obj).attr('id');
    }

    function deselect(obj) {
        $(obj).parent().css("border-left", "none");
    }

    function displayRenderLoader() {
        $('#viewer .preloader-wrapper').addClass('active');
        $("#viewer-placeholder").css('display', 'block');
    }

    function hideRenderLoader() {
        $('#viewer .preloader-wrapper').removeClass('active');
        $("#viewer-placeholder").css('display', 'none');
    }

    function displayDownloadLoader() {
        $('#buttons .preloader-wrapper').addClass('active');
    }

    function hideDownloadLoader() {
        $('#buttons .preloader-wrapper').removeClass('active');
    }

    function resetParameters() {
        // Reset basic inputs : text and number
        $('#renderForm input[type="text"], #renderForm input[type="number"]').each(function () {
            $(this).val($(this).data('default'));
        });

        // Reset dropdown lists (select)
        $('#renderForm select').each(function () {
            // Loop through each option
            $(this).find('option').each(function () {
                $(this).removeAttr('selected');
                // If it's the default one
                if ($(this).data('default') === "selected") {
                    $(this).prop('selected', true);
                }
            });
        });

        $('#renderForm input[type="checkbox"]').each(function () {
            if ($(this).data('default') === "checked") {
                // Not checked but should be
                $(this).prop('checked', true);
            } else {
                // Checked but shouldn't be
                $(this).prop('checked', false);
            }
        });
    }

    // Automatic render on load
    // Filter plugin (blur...)
    if ($('#render').hasClass('OfxImageEffectContextFilter')) {
        renderFilter($("#render.OfxImageEffectContextFilter").attr("pluginId"));
    } else if ($('#render').hasClass('OfxImageEffectContextGenerator')) {
        // Generator plugin (color wheel...)
        renderGenerator($("#render.OfxImageEffectContextGenerator").attr("pluginId"));
    }

    // Manual render on button click
    $("#render.OfxImageEffectContextFilter").click(function () {
        renderFilter($(this).attr("pluginId"));
    });
    $("#render.OfxImageEffectContextGenerator").click(function () {
        renderGenerator($(this).attr("pluginId"));
    });

    // Send an image from an external URL
    $("#renderUrl.OfxImageEffectContextFilter").click(function(){
        fromUrlRender($(this).attr("pluginId"));
        $("#imgUrl").parent().css("border-left", "solid 10px rgb(0,150,136)").css("color", "white");
        $(".sampleImage").each(function () {
            deselect($(this));
        });

    });

    // Reset button
    $('#reset').click(function () {
        resetParameters();
    });


    $("#addGalleryImage").click(function(event){

        $("#download-view").addClass('disabled');
        $("#addGalleryImage").addClass('disabled');
        $("#render").addClass('disabled');

        var pluginId = $("#addGalleryImage").attr("pluginId");
        var renderId = $("#renderedPic").attr("src").split("/resource/")[0].split("/render/")[1];
        var resourceId = $("#renderedPic").attr("src").split("/resource/")[1];

        $.ajax({
                type: "POST",
                url: "/plugin/" + pluginId + "/render/" + renderId + "/resource/" + resourceId,
                async: false //avoid an empty data when result is returned.
            }).done(function(){
                $("#download-view").removeClass('disabled');
                $("#render").removeClass('disabled');
            })
    }); //.off("click");

    /* Before / After slider */

    function init_beforeAfterSlider() {
        if (!$('#BeforeAfterSlider').is(":visible")) {
            $('#BeforeAfterSlider').noUiSlider({
                start: 50,
                step: 1,
                direction: 'ltr',
                orientation: 'horizontal',
                behaviour: 'tap-drag',
                range: {
                    'min': 0,
                    'max': 100
                }
            }).fadeIn(500);

            $(".noUi-handle").after("<div id=\"original-label\">Original picture</div>");
            $(".noUi-handle").after("<div id=\"render-label\">Rendered picture</div>");
            $("#original-label").css({
                "margin-left": "-130px",
                "margin-top": "-35px",
                "position": "absolute"
            });
            $("#render-label").css({
                "margin-top": "-35px",
                "position": "absolute",
                "margin-left": "10px"
            });

            reload_beforeAfterRender();
        }

        $('#BeforeAfterSlider div.noUi-handle').mousedown(function () {
            $(document).mousemove(function (event) {
                if ($('#BeforeAfterSlider').val() >= 75) {
                    $("#render-label").fadeOut(200);
                }
                else if ($('#BeforeAfterSlider').val() <= 25) {
                    $("#original-label").fadeOut(200);
                }
                else {
                    $("#render-label").fadeIn(200);
                    $("#original-label").fadeIn(200);
                }
                change_beforeAfterRender($('#BeforeAfterSlider').val());
            });
        });
    }

    function change_beforeAfterRender(value) {
        originalPicW = (value / 100) * $("#viewer img#renderedPic").width();
        $("#viewer img#originalPic").css("clip", "rect(0 " + originalPicW + "px auto 0)");
    }

    function reload_beforeAfterRender() {
        $('#BeforeAfterSlider').val(50, {set: true});
        change_beforeAfterRender(50);
    }

    /* Resize originalPic on resize of window */
    var rtime;
    var timeout = false;
    var delta = 200;
    $(window).resize(function() {
        $("#viewer img#originalPic").fadeOut(200);
        rtime = new Date();
        if (timeout === false) {
            timeout = true;
            setTimeout(resizeend, delta);
        }
    });

    function resizeend() {
        if (new Date() - rtime < delta) {
            setTimeout(resizeend, delta);
        } else {
            timeout = false;
            $("#viewer img#originalPic").css("width", $("#viewer img#renderedPic").width());
            offset = $("#viewer img#renderedPic").offset;
            $("#viewer img#originalPic").offset({ top: offset.top, left: offset.left})
            .fadeIn(200);

            change_beforeAfterRender($('#BeforeAfterSlider').val());
        }               
    }

});
