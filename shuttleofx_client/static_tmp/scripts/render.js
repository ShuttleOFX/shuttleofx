$(document).ready(function() {

    function formToJson()
    {
        var renderParameters = [];
        $("input", $('#renderForm')).each(function(index){
            var jsonForm={};
            switch($(this).attr("ofxType")) {
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
                    }else{
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

        $("select", $('#renderForm')).each(function(index){
            var jsonForm={};
            jsonForm["id"] = $(this).attr("id");
            jsonForm["value"] = this.value;
            renderParameters.push(jsonForm);
        });

        return renderParameters;
    }

    function renderGenerator(pluginId){
        displayLoader();
        var renderParameters = formToJson();

        $.ajax({
            type: "POST",
            url: "/render",
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify({
                nodes: [{
                    id: 0,
                    plugin: pluginId,
                    parameters: renderParameters
                },{
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
                options:[],
            }),
        })
        .done(function(data){
            $("#viewer img#renderedPic").attr("src", "/render/" + data.render.id + "/resource/" + data.render.outputFilename);
            $("#download-view").removeClass('disabled');
            hideLoader();
            $('.display img').css({height: "auto"});

             $("#downloadtrigger").click(function(data){
               $.ajax({
                    type: "POST",
                    url: "/render",
                    contentType: 'application/json; charset=utf-8',
                    data: JSON.stringify({
                        nodes: [{
                            id: 0,
                            plugin: pluginId,
                            parameters: renderParameters
                        },{
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
                        options:[],
                    }),
        })
        .done(function(data){
                    var link = document.createElement("a");
                    link.download = name;
                    link.href = "/render/" + data.render.id + "/resource/" + data.render.outputFilename;
                    link.click();
                    $("#downloadModal").modal('hide');
                });
            });
        })
        .error(function(data){
            console.log('POST ERROR !');
        });
    }

    function renderFilter(pluginId){
        displayLoader();
        var renderParameters = formToJson();

        $.ajax({
            type: "POST",
            url: "/render",
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify({
                nodes: [{
                    id: 0,
                    plugin: "tuttle.pngreader",
                    parameters: [
                        {
                            "id" : "filename",
                            "value" : "{RESOURCES_DIR}/"+ selectedResource
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
        .done(function(data){
			$("#viewer img#originalPic").attr("src", "/resource/" + selectedResource);
        	$("#viewer img#originalPic").show();
        	$("#viewer img#renderedPic").attr("src", "/render/" + data.render.id + "/resource/" + data.render.outputFilename);
            $("#download-view").removeClass('disabled');
            hideLoader();
            $('.display img').css({height: "auto"});
        	init_beforeAfterSlider();

             $("#downloadtrigger").click(function(data){
               $.ajax({
            type: "POST",
            url: "/render",
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify({
                nodes: [{
                    id: 0,
                    plugin: "tuttle.pngreader",
                    parameters: [
                        {
                            "id" : "filename",
                            "value" : "{RESOURCES_DIR}/"+ selectedResource
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
        .done(function(data){
                    var link = document.createElement("a");
                    link.download = name;
                    link.href = "/render/" + data.render.id + "/resource/" + data.render.outputFilename;
                    link.click();
                    $("#downloadModal").modal('hide');
                });
            });
        })
        .error(function(data){
            console.log('POST ERROR !');
        });
    }

    var allResources = undefined;
    var selectedResource = undefined;

    $.ajax({
        type: "GET",
        url: "/resource",
        async: false, //avoid an empty data when result is returned.
    })
    .done(function(data){
        allResources = [];

        $.each( data.resources, function( index, resource){
            allResources.push(resource['_id']['$oid']);
        });

        if(allResources !== undefined && allResources.length > 0){
            selectedResource = allResources[0];
        }
    })
    .error(function(data){
        console.log('POST ERROR !');
    });

    $(".sampleImage").each(function() {
        $(this).click(function(){
            setResourceSelected($(this));
            var pluginId = $("#render.OfxImageEffectContextFilter").attr("pluginId");
            renderFilter(pluginId);
        });
    });

    function setResourceSelected(obj){
        $(".sampleImage").each(function() {
            deselect($(this));
        });
        $(obj).parent().css("border", "solid 2px gray");
        selectedResource = $(obj).attr('id');
    }

    function deselect(obj){
        $(obj).parent().css("border", "");
    }

    function displayLoader(){
        $('#viewer .preloader-wrapper').addClass('active');
        $("#viewer-placeholder").css('display', 'block');
    }

    function hideLoader(){
        $('#viewer .preloader-wrapper').removeClass('active');
        $("#viewer-placeholder").css('display', 'none');
    }

    function resetParameters () {
        // Reset basic inputs : text and number
        $('#renderForm input[type="text"], #renderForm input[type="number"]').each(function() {
            $(this).val($(this).data('default'));
        });

        // Reset dropdown lists (select)
        $('#renderForm select').each(function() {
            // Loop through each option
            $(this).find('option').each(function() {
                $(this).removeAttr('selected');
                // If it's the default one
                if ($(this).data('default') === "selected") {
                    $(this).prop('selected', true);
                }
            });
        });

        $('#renderForm input[type="checkbox"]').each(function() {
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
    } else if($('#render').hasClass('OfxImageEffectContextGenerator')) {
        // Generator plugin (color wheel...)
        renderGenerator($("#render.OfxImageEffectContextGenerator").attr("pluginId"));
    }

    // Manual render on button click
    $("#render.OfxImageEffectContextFilter").click(function(){
        renderFilter($(this).attr("pluginId"));
    });
    $("#render.OfxImageEffectContextGenerator").click(function(){
        renderGenerator($(this).attr("pluginId"));
    });

    // Reset button
    $('button#reset').click(function() {
        resetParameters();
    });

/* Before / After slider */

function init_beforeAfterSlider() {
  if (!$('#BeforeAfterSlider').is(":visible")) {
    $('#BeforeAfterSlider').noUiSlider({
      start : 50,
      step: 1,
      direction: 'ltr',
      orientation: 'horizontal',
      behaviour: 'tap-drag',
      range : {
        'min' : 0,
        'max' : 100
      }
    }).fadeIn(500);
  }
  reload_beforeAfterRender();
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

  $('#BeforeAfterSlider div.noUi-handle').mousedown(function() {
    $(document).mousemove(function(event) {
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
  originalPicW = (value/100) * $("#viewer img#renderedPic").width();
  $("#viewer img#originalPic").css("clip", "rect(0 " + originalPicW + "px auto 0)");
}

function reload_beforeAfterRender() {
  $('#BeforeAfterSlider').val(50, { set: true });
  change_beforeAfterRender(50);
}

});