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
                    value: "{UNIQUE_OUTPUT_FILE}" + ".png"
                }

                ]
            }],

            connections: [{
                    src: {id: 0},
                    dst: {id: 1}
            }],
        }),
    })
    .done(function(data){
        console.log('POST DONE !');
        $("#viewer img").attr("src", "/render/" + data.render.id + "/resource/" + data.render.outputFilename);
        $("#download-view").attr("href", "/render/" + data.render.id + "/resource/" + data.render.outputFilename);
        $("#download-view").removeClass('disabled');
        $("#viewer-placeholder").css('display', 'none');
        $('.display img').css({height: "auto"});
    })
    .error(function(data){
        console.log('POST ERROR !');
    })
});

$("#render.OfxImageEffectContextFilter").click(function(){
    var pluginId = $(this).attr("pluginId");
    console.log('Filter: ' + pluginId );
    var renderParameters = formToJson();

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
                        "value" : "/tmp/lol.png"
                    }
                ]
            },{
                id: 1,
                plugin: pluginId,
                parameters: renderParameters
            },{
                id: 2,
                plugin: "tuttle.pngwriter",
                parameters: []
            }],

            connections: [{
                src: {id: 0},
                dst: {id: 1}
            },{
                src: {id: 1},
                dst: {id: 2}
            }],
            renderNode: {id: 2}
        }),
    })
    .done(function(data){
        console.log('POST DONE !');
        $("#viewer img").attr("src", "/render/" + data.render.id + "/resource/" + data.render.outputFilename);
        $("#download-view").attr("href", "/render/" + data.render.id + "/resource/" + data.render.outputFilename);
        $("#download-view").removeClass('disabled');
        $("#viewer-placeholder").css('display', 'none');
        $('.display img').css({height: "auto"});
    })
    .error(function(data){
        console.log('POST ERROR !');
    })
});

});
