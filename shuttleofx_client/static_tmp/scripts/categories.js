/********************************************
    Categories tree view :
      - Ajax call to get data
      - Generate HTML from data
      - Handle events to expand/minimize
********************************************/
$(document).ready(function() {
    $("#left-nav ul div#categories").on('click', 'ul li i.folder',function(){
        var category = $(this).next('a').text(); // get category name

        $(this).parent().children('ul').slideToggle(300, function(){
            // If the category has been opened
            if($(this).is(':visible')){
                // Update list of opened category
                addOpenCategory(category);
            } else {
                removeOpenCategory(category);
            }
        });

        $(this).toggleClass('fa-folder-open', 'fa-folder');
    });
});

var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

$.ajax({
    url: '/plugins',
    type: 'GET',
})
.done(function(data) {
    var categoryTree = [];
    var object = {};

    for (var i = 0; i < data.plugins.length; i++) {
        if (data.plugins[i].properties.OfxImageEffectPluginPropGrouping) {
            var group = data.plugins[i].properties.OfxImageEffectPluginPropGrouping.value;
            var splittedPath = group.split("/");

            splittedPath.reduce(function(o, s){
                return o[s] = [];
            }, object);

            // Merge all arrays to create one
            $.extend(true, categoryTree, object);
        }
    }

    var html = generateHtmlFromCategoriesTree(categoryTree, '');
    $('#categories').append(html);
    // When all categories are loaded and append,
    // re-open the ones that were opened on the previous page
    autoOpenCategories();
});

function generateHtmlFromCategoriesTree(object, previous){
    var urlCategory = getUrlParameter('search');
    var pluginCategory = $("#grouping").attr("attr-grouping");
    var linkClass = "";
    var html = '<ul>';
    for (var i = 0; i < Object.keys(object).length; i++) {
        var link = previous;
        // Do not add a / if it's the root element
        if (link.length === 0) {
            link += '/category?search=' + Object.keys(object)[i];
        } else {
            link += '/' + Object.keys(object)[i];
        }

                //if current url matches the category
        if (urlCategory == link.split("/category?search=")[1]){
            linkClass ="class = 'activeCategory'";
        }else{
            linkClass = "";
        }

        if ($.isEmptyObject(object[Object.keys(object)[i]])) {
            html += '<li><i class="nofolder fa fa-fw"> - </i><a href="'+ link + '"'+linkClass+'>' + Object.keys(object)[i] + '</a>';
        } else {
            html += '<li><i class="folder fa fa-fw fa-folder"></i><a href="'+ link + '"'+linkClass+'>' + Object.keys(object)[i] + '</a>';
            html += generateHtmlFromCategoriesTree(object[Object.keys(object)[i]], link);
        }
        html += '</li>';
    }
    html += '</ul>';
    return html;
}

function addOpenCategory(categoryName){
    if (!Cookies.get("open_categories")) {
        Cookies.set("open_categories", categoryName, { expires: 1, path: "/" });
    } else {
        Cookies.set("open_categories", Cookies.get("open_categories") + "," + categoryName);
    }
}

function autoOpenCategories(){
    if (Cookies.get("open_categories")) {
        var openedCategories = Cookies.get("open_categories").split(",");
        // Loop through each category and open it, if it's in the array of opened categories
        $("#left-nav ul div#categories ul li").each(function(index) {
            if ( openedCategories.indexOf( $(this).children('a').text() ) > -1) {
                $(this).children('ul').show();
                $(this).children('i').toggleClass('fa-folder-open', 'fa-folder');
            };
        });
    }
}

function removeOpenCategory(categoryName){
    var openedCategories = Cookies.get("open_categories").split(",");
    var index = openedCategories.indexOf(categoryName);
    if (index > -1) {
        openedCategories.splice(index, 1);
        openedCategories.join()
        Cookies.set("open_categories", openedCategories.join());
    };
}
