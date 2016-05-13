function updateSortingPrefs(){
  var currentUrl = window.location.href;
  var decomposedUrl = currentUrl.split("?");

  var search ; // keyword in search field
  var count = 20; // number of plugin per page default = 20
  var skip = 1; // number of current page default = 1
  var alphaSort = 1; // alphabetical ordered by default
  var totalPlugins = $("#totalPlugins").val(); // number of plugins return by the search 

  var page = decomposedUrl[0].split("/"); // page plugin or category
  page = page[ page.length - 1 ];

  // get parameters in url and put them in count, skip and search
  if (typeof decomposedUrl[1] != "undefined") {
    decomposedUrl = decomposedUrl[1].split("&");
    var params = [];

    for (var i = 0; i < decomposedUrl.length; i++) {
      var tmp = decomposedUrl[i].split("=");
      var key = tmp[0];
      var val = tmp[1];
      params[key] = val;
    }

    if (typeof params["search"] != "undefined") search = params["search"];
    if (typeof params["skip"] != "undefined") skip = params["skip"];
    if (typeof params["count"] != "undefined") count = params["count"];
    if (typeof params["alphaSort"] != "undefined") alphaSort = params["alphaSort"];
  }

  // Update cookie with new parameters
  cookieManager({"page": page, "search": search, "count": count, "skip":skip, "alphaSort": alphaSort});

  // Change number of plugin per page
  $('select#pageSize').change(function(){
    count = $(this).val();
    var maxPage = Math.ceil(totalPlugins/$('select#pageSize').val());
    if (skip > maxPage) {
      skip = maxPage;
    }

    cookieManager({"count": count, "skip": skip});

    var newUrl = "/" + page + "?";

    if (typeof search != "undefined") {
      newUrl += "search=" + search +"&";
    }

    newUrl += "count=" + count + "&skip=" + skip;

    if (typeof alphaSort != "undefined") {
      newUrl += "&alphaSort=" + alphaSort;
    }

    window.location.href = newUrl;
  });

  // Change sorting preferences
  $('.order-catag label').on('click', function() {
    alphaSort = -alphaSort;

    cookieManager({"count": count, "skip": skip, "alphaSort": alphaSort});

    var newUrl = "/" + page + "?";

    if (typeof search != "undefined") {
      newUrl += "search=" + search +"&";
    }

    newUrl += "count=" + count + "&skip=" + skip;

    if (typeof alphaSort != "undefined") {
      newUrl += "&alphaSort=" + alphaSort;
    }

    window.location.href = newUrl;
  });
}


// Manage User sorting preferences inside cookies 
// count --> number of plugins to be displayed
// skip --> on which page is the user
function cookieManager(value){
  if (!Cookies.get("user_sorting_prefs")) {
    Cookies.set("user_sorting_prefs", value, { expires: 30, path: "/" });
  } else {
    Cookies.set("user_sorting_prefs", value);
  }
}

/**
 * Update link given user's sorting preferences
 * @param  {DOM element} link         link element ex : $("#back-to-plugins")
 * @param  {boolean} override         override default href or complete it
 */
function updateLinkWithUserSortingPrefs(link, override){
  var prefs = Cookies.getJSON("user_sorting_prefs");
  if (prefs == undefined) return;

  var count = prefs.count,
      skip = prefs.skip,
      search = prefs.search,
      page = prefs.page,
      alphaSort = prefs.alphaSort;
  var hrefValue;

  if (override) {
    if(search){
      hrefValue = "/" + page + "?search=" + search + "&count=" + count + "&skip=" + skip + "&alphaSort=" + alphaSort;
    } else {
      hrefValue = "/" + page + "?count=" + count + "&skip=" + skip  + "&alphaSort=" + alphaSort;
    }
  } else {
      var href = link.attr('href');
      // Simple case here, we only add infos needed for pagination
      hrefValue = href + "?count=" + count + "&skip=" + skip  + "&alphaSort=" + alphaSort;
  }
  link.attr("href", hrefValue);
}

// disable clic on object with class disabled
$("li.disabled a").click(function(e){
  e.preventDefault();
  return;
});
