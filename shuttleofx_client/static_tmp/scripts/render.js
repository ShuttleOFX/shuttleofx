$(document).ready(function() {

function formToJson()
{
    var renderParameters = [];
    $("input", $('#renderForm')).each(function(index){
        var jsonForm={};
        // console.log(this.type);
        switch($(this).attr("ofxType")) {
            case 'OfxParamTypeInteger':
                jsonForm["id"] = $(this).attr("id");
                jsonForm["value"] = parseInt(this.value);
                renderParameters.push(jsonForm);
                break;
            case 'OfxParamTypeInteger2D':
                var tab = [];
                tab.push(4);
                tab.push(4);
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
                };
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



$("#render.OfxImageEffectContextGenerator").click(function(){
    
    var pluginId = $(this).attr("pluginId");
    console.log('Generator: ' + pluginId );
    var renderParameters = formToJson();

    // $('#resultForm').text(JSON.stringify(renderParameters));

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
        console.log('POST DONE !');
        $("#viewer img").attr("src", "/render/" + data.render.id + "/resource/" + data.render.outputFilename);
        $("#download-view").removeClass('disabled');
        $("#viewer-placeholder").css('display', 'none');
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
                $("#downloadModal").modal('hide')
            })
        })
    })
    .error(function(data){
        console.log('POST ERROR !');
    })
});

$("#render.OfxImageEffectContextFilter").click(function(){
    var pluginId = $(this).attr("pluginId");
    renderFilter(pluginId)
});


function renderFilter(pluginId){
    var renderParameters = formToJson();
    console.log('Filter: ' + pluginId );
    console.log(renderParameters);

    // $('#resultForm').text(JSON.stringify(renderParameters));

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
        console.log('POST DONE !');
        $("#viewer img").attr("src", "/render/" + data.render.id + "/resource/" + data.render.outputFilename);
        $("#download-view").removeClass('disabled');
        $("#viewer-placeholder").css('display', 'none');
        $('.display img').css({height: "auto"});

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
                $("#downloadModal").modal('hide')
            })
        })
    })
    .error(function(data){
        console.log('POST ERROR !');
    })
}

var allResources = undefined;
var selectedResource = undefined;

$.ajax({
    type: "GET",
    url: "/resource",
    async: false, //avoid an empty data when result is returned.
})
.done(function(data){
    allResources = []

    $.each( data.resources, function( index, resource){
        allResources.push(resource['_id']['$oid']);
    });

    if(allResources != undefined && allResources.length > 0){
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
        console.log($("#render.OfxImageEffectContextFilter"))
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


});