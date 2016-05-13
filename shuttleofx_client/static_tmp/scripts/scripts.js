/* Modernizr 2.7.1 (Custom Build) | MIT & BSD */
;window.Modernizr=function(a,b,c){function A(a){j.cssText=a}function B(a,b){return A(m.join(a+";")+(b||""))}function C(a,b){return typeof a===b}function D(a,b){return!!~(""+a).indexOf(b)}function E(a,b){for(var d in a){var e=a[d];if(!D(e,"-")&&j[e]!==c)return b=="pfx"?e:!0}return!1}function F(a,b,d){for(var e in a){var f=b[a[e]];if(f!==c)return d===!1?a[e]:C(f,"function")?f.bind(d||b):f}return!1}function G(a,b,c){var d=a.charAt(0).toUpperCase()+a.slice(1),e=(a+" "+o.join(d+" ")+d).split(" ");return C(b,"string")||C(b,"undefined")?E(e,b):(e=(a+" "+p.join(d+" ")+d).split(" "),F(e,b,c))}var d="2.7.1",e={},f=!0,g=b.documentElement,h="modernizr",i=b.createElement(h),j=i.style,k,l={}.toString,m=" -webkit- -moz- -o- -ms- ".split(" "),n="Webkit Moz O ms",o=n.split(" "),p=n.toLowerCase().split(" "),q={svg:"http://www.w3.org/2000/svg"},r={},s={},t={},u=[],v=u.slice,w,x=function(a,c,d,e){var f,i,j,k,l=b.createElement("div"),m=b.body,n=m||b.createElement("body");if(parseInt(d,10))while(d--)j=b.createElement("div"),j.id=e?e[d]:h+(d+1),l.appendChild(j);return f=["&#173;",'<style id="s',h,'">',a,"</style>"].join(""),l.id=h,(m?l:n).innerHTML+=f,n.appendChild(l),m||(n.style.background="",n.style.overflow="hidden",k=g.style.overflow,g.style.overflow="hidden",g.appendChild(n)),i=c(l,a),m?l.parentNode.removeChild(l):(n.parentNode.removeChild(n),g.style.overflow=k),!!i},y={}.hasOwnProperty,z;!C(y,"undefined")&&!C(y.call,"undefined")?z=function(a,b){return y.call(a,b)}:z=function(a,b){return b in a&&C(a.constructor.prototype[b],"undefined")},Function.prototype.bind||(Function.prototype.bind=function(b){var c=this;if(typeof c!="function")throw new TypeError;var d=v.call(arguments,1),e=function(){if(this instanceof e){var a=function(){};a.prototype=c.prototype;var f=new a,g=c.apply(f,d.concat(v.call(arguments)));return Object(g)===g?g:f}return c.apply(b,d.concat(v.call(arguments)))};return e}),r.flexbox=function(){return G("flexWrap")},r.canvas=function(){var a=b.createElement("canvas");return!!a.getContext&&!!a.getContext("2d")},r.rgba=function(){return A("background-color:rgba(150,255,150,.5)"),D(j.backgroundColor,"rgba")},r.backgroundsize=function(){return G("backgroundSize")},r.borderradius=function(){return G("borderRadius")},r.boxshadow=function(){return G("boxShadow")},r.cssanimations=function(){return G("animationName")},r.csstransforms=function(){return!!G("transform")},r.csstransforms3d=function(){var a=!!G("perspective");return a&&"webkitPerspective"in g.style&&x("@media (transform-3d),(-webkit-transform-3d){#modernizr{left:9px;position:absolute;height:3px;}}",function(b,c){a=b.offsetLeft===9&&b.offsetHeight===3}),a},r.csstransitions=function(){return G("transition")},r.video=function(){var a=b.createElement("video"),c=!1;try{if(c=!!a.canPlayType)c=new Boolean(c),c.ogg=a.canPlayType('video/ogg; codecs="theora"').replace(/^no$/,""),c.h264=a.canPlayType('video/mp4; codecs="avc1.42E01E"').replace(/^no$/,""),c.webm=a.canPlayType('video/webm; codecs="vp8, vorbis"').replace(/^no$/,"")}catch(d){}return c},r.audio=function(){var a=b.createElement("audio"),c=!1;try{if(c=!!a.canPlayType)c=new Boolean(c),c.ogg=a.canPlayType('audio/ogg; codecs="vorbis"').replace(/^no$/,""),c.mp3=a.canPlayType("audio/mpeg;").replace(/^no$/,""),c.wav=a.canPlayType('audio/wav; codecs="1"').replace(/^no$/,""),c.m4a=(a.canPlayType("audio/x-m4a;")||a.canPlayType("audio/aac;")).replace(/^no$/,"")}catch(d){}return c},r.svg=function(){return!!b.createElementNS&&!!b.createElementNS(q.svg,"svg").createSVGRect};for(var H in r)z(r,H)&&(w=H.toLowerCase(),e[w]=r[H](),u.push((e[w]?"":"no-")+w));return e.addTest=function(a,b){if(typeof a=="object")for(var d in a)z(a,d)&&e.addTest(d,a[d]);else{a=a.toLowerCase();if(e[a]!==c)return e;b=typeof b=="function"?b():b,typeof f!="undefined"&&f&&(g.className+=" "+(b?"":"no-")+a),e[a]=b}return e},A(""),i=k=null,function(a,b){function l(a,b){var c=a.createElement("p"),d=a.getElementsByTagName("head")[0]||a.documentElement;return c.innerHTML="x<style>"+b+"</style>",d.insertBefore(c.lastChild,d.firstChild)}function m(){var a=s.elements;return typeof a=="string"?a.split(" "):a}function n(a){var b=j[a[h]];return b||(b={},i++,a[h]=i,j[i]=b),b}function o(a,c,d){c||(c=b);if(k)return c.createElement(a);d||(d=n(c));var g;return d.cache[a]?g=d.cache[a].cloneNode():f.test(a)?g=(d.cache[a]=d.createElem(a)).cloneNode():g=d.createElem(a),g.canHaveChildren&&!e.test(a)&&!g.tagUrn?d.frag.appendChild(g):g}function p(a,c){a||(a=b);if(k)return a.createDocumentFragment();c=c||n(a);var d=c.frag.cloneNode(),e=0,f=m(),g=f.length;for(;e<g;e++)d.createElement(f[e]);return d}function q(a,b){b.cache||(b.cache={},b.createElem=a.createElement,b.createFrag=a.createDocumentFragment,b.frag=b.createFrag()),a.createElement=function(c){return s.shivMethods?o(c,a,b):b.createElem(c)},a.createDocumentFragment=Function("h,f","return function(){var n=f.cloneNode(),c=n.createElement;h.shivMethods&&("+m().join().replace(/[\w\-]+/g,function(a){return b.createElem(a),b.frag.createElement(a),'c("'+a+'")'})+");return n}")(s,b.frag)}function r(a){a||(a=b);var c=n(a);return s.shivCSS&&!g&&!c.hasCSS&&(c.hasCSS=!!l(a,"article,aside,dialog,figcaption,figure,footer,header,hgroup,main,nav,section{display:block}mark{background:#FF0;color:#000}template{display:none}")),k||q(a,c),a}var c="3.7.0",d=a.html5||{},e=/^<|^(?:button|map|select|textarea|object|iframe|option|optgroup)$/i,f=/^(?:a|b|code|div|fieldset|h1|h2|h3|h4|h5|h6|i|label|li|ol|p|q|span|strong|style|table|tbody|td|th|tr|ul)$/i,g,h="_html5shiv",i=0,j={},k;(function(){try{var a=b.createElement("a");a.innerHTML="<xyz></xyz>",g="hidden"in a,k=a.childNodes.length==1||function(){b.createElement("a");var a=b.createDocumentFragment();return typeof a.cloneNode=="undefined"||typeof a.createDocumentFragment=="undefined"||typeof a.createElement=="undefined"}()}catch(c){g=!0,k=!0}})();var s={elements:d.elements||"abbr article aside audio bdi canvas data datalist details dialog figcaption figure footer header hgroup main mark meter nav output progress section summary template time video",version:c,shivCSS:d.shivCSS!==!1,supportsUnknownElements:k,shivMethods:d.shivMethods!==!1,type:"default",shivDocument:r,createElement:o,createDocumentFragment:p};a.html5=s,r(b)}(this,b),e._version=d,e._prefixes=m,e._domPrefixes=p,e._cssomPrefixes=o,e.testProp=function(a){return E([a])},e.testAllProps=G,e.testStyles=x,e.prefixed=function(a,b,c){return b?G(a,b,c):G(a,"pfx")},g.className=g.className.replace(/(^|\s)no-js(\s|$)/,"$1$2")+(f?" js "+u.join(" "):""),e}(this,this.document),function(a,b,c){function d(a){return"[object Function]"==o.call(a)}function e(a){return"string"==typeof a}function f(){}function g(a){return!a||"loaded"==a||"complete"==a||"uninitialized"==a}function h(){var a=p.shift();q=1,a?a.t?m(function(){("c"==a.t?B.injectCss:B.injectJs)(a.s,0,a.a,a.x,a.e,1)},0):(a(),h()):q=0}function i(a,c,d,e,f,i,j){function k(b){if(!o&&g(l.readyState)&&(u.r=o=1,!q&&h(),l.onload=l.onreadystatechange=null,b)){"img"!=a&&m(function(){t.removeChild(l)},50);for(var d in y[c])y[c].hasOwnProperty(d)&&y[c][d].onload()}}var j=j||B.errorTimeout,l=b.createElement(a),o=0,r=0,u={t:d,s:c,e:f,a:i,x:j};1===y[c]&&(r=1,y[c]=[]),"object"==a?l.data=c:(l.src=c,l.type=a),l.width=l.height="0",l.onerror=l.onload=l.onreadystatechange=function(){k.call(this,r)},p.splice(e,0,u),"img"!=a&&(r||2===y[c]?(t.insertBefore(l,s?null:n),m(k,j)):y[c].push(l))}function j(a,b,c,d,f){return q=0,b=b||"j",e(a)?i("c"==b?v:u,a,b,this.i++,c,d,f):(p.splice(this.i++,0,a),1==p.length&&h()),this}function k(){var a=B;return a.loader={load:j,i:0},a}var l=b.documentElement,m=a.setTimeout,n=b.getElementsByTagName("script")[0],o={}.toString,p=[],q=0,r="MozAppearance"in l.style,s=r&&!!b.createRange().compareNode,t=s?l:n.parentNode,l=a.opera&&"[object Opera]"==o.call(a.opera),l=!!b.attachEvent&&!l,u=r?"object":l?"script":"img",v=l?"script":u,w=Array.isArray||function(a){return"[object Array]"==o.call(a)},x=[],y={},z={timeout:function(a,b){return b.length&&(a.timeout=b[0]),a}},A,B;B=function(a){function b(a){var a=a.split("!"),b=x.length,c=a.pop(),d=a.length,c={url:c,origUrl:c,prefixes:a},e,f,g;for(f=0;f<d;f++)g=a[f].split("="),(e=z[g.shift()])&&(c=e(c,g));for(f=0;f<b;f++)c=x[f](c);return c}function g(a,e,f,g,h){var i=b(a),j=i.autoCallback;i.url.split(".").pop().split("?").shift(),i.bypass||(e&&(e=d(e)?e:e[a]||e[g]||e[a.split("/").pop().split("?")[0]]),i.instead?i.instead(a,e,f,g,h):(y[i.url]?i.noexec=!0:y[i.url]=1,f.load(i.url,i.forceCSS||!i.forceJS&&"css"==i.url.split(".").pop().split("?").shift()?"c":c,i.noexec,i.attrs,i.timeout),(d(e)||d(j))&&f.load(function(){k(),e&&e(i.origUrl,h,g),j&&j(i.origUrl,h,g),y[i.url]=2})))}function h(a,b){function c(a,c){if(a){if(e(a))c||(j=function(){var a=[].slice.call(arguments);k.apply(this,a),l()}),g(a,j,b,0,h);else if(Object(a)===a)for(n in m=function(){var b=0,c;for(c in a)a.hasOwnProperty(c)&&b++;return b}(),a)a.hasOwnProperty(n)&&(!c&&!--m&&(d(j)?j=function(){var a=[].slice.call(arguments);k.apply(this,a),l()}:j[n]=function(a){return function(){var b=[].slice.call(arguments);a&&a.apply(this,b),l()}}(k[n])),g(a[n],j,b,n,h))}else!c&&l()}var h=!!a.test,i=a.load||a.both,j=a.callback||f,k=j,l=a.complete||f,m,n;c(h?a.yep:a.nope,!!i),i&&c(i)}var i,j,l=this.yepnope.loader;if(e(a))g(a,0,l,0);else if(w(a))for(i=0;i<a.length;i++)j=a[i],e(j)?g(j,0,l,0):w(j)?B(j):Object(j)===j&&h(j,l);else Object(a)===a&&h(a,l)},B.addPrefix=function(a,b){z[a]=b},B.addFilter=function(a){x.push(a)},B.errorTimeout=1e4,null==b.readyState&&b.addEventListener&&(b.readyState="loading",b.addEventListener("DOMContentLoaded",A=function(){b.removeEventListener("DOMContentLoaded",A,0),b.readyState="complete"},0)),a.yepnope=k(),a.yepnope.executeStack=h,a.yepnope.injectJs=function(a,c,d,e,i,j){var k=b.createElement("script"),l,o,e=e||B.errorTimeout;k.src=a;for(o in d)k.setAttribute(o,d[o]);c=j?h:c||f,k.onreadystatechange=k.onload=function(){!l&&g(k.readyState)&&(l=1,c(),k.onload=k.onreadystatechange=null)},m(function(){l||(l=1,c(1))},e),i?k.onload():n.parentNode.insertBefore(k,n)},a.yepnope.injectCss=function(a,c,d,e,g,i){var e=b.createElement("link"),j,c=i?h:c||f;e.href=a,e.rel="stylesheet",e.type="text/css";for(j in d)e.setAttribute(j,d[j]);g||(n.parentNode.insertBefore(e,n),m(c,0))}}(this,document),Modernizr.load=function(){yepnope.apply(window,[].slice.call(arguments,0))};

// Helper function to display info/error/success messages
function addMessage(content, type) {
	if ($(".message").length >= 1) {
		$(".message").remove();
	}

	if (type == "error") {
		return "<div class=\"message error\"><i class=\"fa fa-meh-o\"></i><p>" + content + "</p></div>";
	}
	else if (type == "success") {
		return "<div class=\"message success\"><i class=\"fa fa-rocket\"></i><p>"+ content + "</p></div>";
	}
      else if(type == "info") {
          return "<div class=\"message info\"><i class=\"fa fa-info-circle\"></i><p>"+ content + "</p></div>";
      }
};
function removeMessage() {
	$(".message").remove();
}

$(".userunloged p a").on("click", function(e){
	$(this).toggleClass("active");
	$(".userunloged div").slideToggle(300);
})


$('.param-more').popover();

$("#searchForm").find("#searchquery").focus(
  function(){
    $(this).width("250px");
    $(this).parent("form").addClass("active");
  }
);
$("#searchForm").find("#searchquery").blur(
  function(){
    $(this).width("200px");
    $(this).parent("form").removeClass("active");
  }
);



$('[data-toggle]').on('click', function() {
  var toggle;

  toggle = $(this).addClass('active').data('toggle');
  $(this).siblings('[data-toggle]').removeClass('active');
  $('.surveys').removeClass('grid list').addClass(toggle);

  // Change the way images are displayed if there is a preview
  $(".surveys li:has(img.custom)").each(function(){
  	var title = $(this).find("h3");
  	var pluginsDiv = $(this).find(".plugins-titles, .plugins-info");

    if (toggle == "list") {
      // In list mode, move h3 to the next div in order to isolate the img
      // so we can have the image on the left and the title and description on the right
  	  title.detach().prependTo($(this).find(".plugins-info"));
  	  pluginsDiv.css({"display": "table-cell", "vertical-align": "middle"}).redrawForWebkit();
  	} else {
  	  // In grid view, go back to the original layout
  	  title.detach().appendTo($(this).find(".plugins-titles"));
  	  pluginsDiv.css({"display": "inline-block", "vertical-align": ""});
  	}
  });
});


$('.order-catag label').on('click', function() {
  var content = $(this).html();

  if ($(this).hasClass('ascendant')) {
  	//send catalog descendant
  	$(this).html('<i class="fa fa-sort-alpha-desc"></i>Descending');
  	$(this).removeClass('ascendant').addClass('descendant');
  }else{
  	//send catalog descendant
  	$(this).html('<i class="fa fa-sort-alpha-asc"></i>Ascending');
  	$(this).removeClass('descendant').addClass('ascendant');

  };

});

function changeVersion(versionNumber) {
  var currentUrl = window.location.href;
  var decomposedUrl = currentUrl.split('/version');

  var newUrl = decomposedUrl[0];

  if (typeof decomposedUrl[1] != 'undefined') {
    var currentTab = currentUrl.split('/');
    currentTab = currentTab[currentTab.length - 1];

    if (!/[a-zA-z]+/.test(currentTab)) {
      window.location.href = newUrl + '/version/' + versionNumber.options[versionNumber.selectedIndex].value;
      return;
    };
    window.location.href = newUrl + '/version/' + versionNumber.options[versionNumber.selectedIndex].value + '/' + currentTab;
    return;
  }
  window.location.href = newUrl + '/version/' + versionNumber.options[versionNumber.selectedIndex].value;
  return;
}

// Force webkit browsers to redraw style changes
// see : http://stackoverflow.com/a/3485654
(function($) {
    $.fn.redrawForWebkit = function() {
        this[0].style.display = 'none';
        this[0].offsetHeight;
        this[0].style.display = 'table-cell';
    };
})(jQuery);


/*
* Bamboo.js - minimal responsive javascript framework
* Author: Andrew Greig
* Copyright (c) 2013 Andrew Greig
* Dual MIT/BSD license
*/

var Bamboo = (function (window, document) {

	var container = $('#container').length == 0 ? $('#homeContainer') : $('#container')

	var
	// objects
	openButton = $('.open'),
	cover = null,

	// Browser checks
	hasTouch = testTouch(),
	offset = testOffset(),
	has3d = has3d(),
	// Helpers
	translateZ = has3d ? ' translateZ(0)' : '',

	// Events
	resizeEvent = 'onorientationchange' in window ? 'orientationchange' : 'resize',
	startEvent = hasTouch ? 'touchstart' : 'mousedown',
	moveEvent = hasTouch ? 'touchmove' : 'mousemove',
	endEvent = hasTouch ? 'touchend' : 'mouseup',
	cancelEvent = hasTouch ? 'touchcancel' : 'mouseup',

	Bamboo = function (opts) {

		var _this = this;

		this.options = {
			menu: true,
			breakpoint: 768,
		    menuWidth: 265,
		    headerHeight: 0,
		    snapThreshold: null,
		    resize: null
		};


		// Options from user
		for (i in opts) this.options[i] = opts[i];

		this.resizeSite();

		// add required html
		cover = $('<div id="cover" />');
		container.find('#scroller').append(cover);

		// event listeners
		$(window).on(resizeEvent, this.resizeSite.bind(this) );
		container.on(startEvent, this._start.bind(this) );
		container.on(moveEvent, this._move.bind(this) );
		container.on(endEvent, this._end.bind(this) );

	}

	Bamboo.prototype = {

		info : {},

		x : 0,		// starting point
	    dx : 0,		// distance moved
	    ox : null,	// original X
	    tgt: null,	// menu tap target
	    desktop: false,

	    // returns page dimensions in array
	    dimensions: function(){
	    	return [this.info.docWidth, this.info.docHeight];
	    },

	    offset: function(){
	    	return offset;
	    },

	    // function to resize site
	    resizeSite: function() {
			// get page sizes
			this.info.docHeight = $(window).height();
			this.info.docWidth = $(window).width();
			this.layout();
			// snap
			this.snapThreshold = this.options.snapThreshold === null ?
				Math.round(this.info.docWidth * 0.25) :
				/%/.test(this.options.snapThreshold) ?
					Math.round(this.info.docWidth * this.options.snapThreshold.replace('%', '') / 100) :
					this.options.snapThreshold;
			// resize callback
			if (this.options.resize) {
				this.options.resize();
			}
	    },

	    // set layout sizes
	    layout: function(){
	    	// mobile / tablet
	    	if (this.info.docWidth < this.options.breakpoint) {
	    		this.desktop = false;
				// container
	    		// container.css({ width : this.info.docWidth, height : 'auto' });
		    	// scoller height
				// container.find('#scroller').css({ height : this.info.docHeight + offset});
	    	// desktop
	    	} else {
	    		this.desktop = true;
	    		// container
	    		container.css({
	    			width : this.info.docWidth - this.options.menuWidth,
	    			// height : this.info.docHeight + offset
	    		});
	    		// scoller height
				// container.find('#scroller').css({ height : 'auto' });
	    	}
			// hide address bar
			this.hideAddressBar();
		},

		// hide the ios address bar
	    hideAddressBar: function() {
			setTimeout( function(){ window.scrollTo(0, 1); }, 50 );
		},

	    /**
		* Pseudo private methods
		*/

		_start: function(e) {
			if (this.initiated) return;	// if already started
			if (this.desktop || !this.options.menu) return; // if menu not applicable

			$('#console').html('start')
			var point = hasTouch ? e.originalEvent.touches[0] : e;

			this.initiated = true;
			this.pointX = point.pageX;
			this.pointY = point.pageY;
			this.stepsX = 0;
			this.stepsY = 0;
			this.directionLocked = false;

			this.x = container.offset().left;
			this.ox = -this.x + this.pointX;
			this.tgt = $(e.target);
			container.css({ 'transition-duration' : '0s' });
		},

		_move: function(e) {
			if (!this.initiated) return;
			if (this.desktop || !this.options.menu) return; // if menu not applicable

			$('#console').html('move')
			var point = hasTouch ? e.originalEvent.touches[0] : e;

			this.stepsX += Math.abs(point.pageX - this.pointX);
			this.stepsY += Math.abs(point.pageY - this.pointY);

			// We take a 10px buffer to figure out the direction of the swipe
			if (this.stepsX < 10 && this.stepsY < 10) {
				return;
			}

			// We are scrolling vertically, so skip SwipeView and give the control back to the browser
			if (!this.directionLocked && this.stepsY > this.stepsX) {
				this.initiated = false;
				return;
			}

			e.preventDefault();
			this.directionLocked = true;

			if(this.ox){
				var nx = parseInt(point.pageX) - this.ox;
				this.dx = nx - this.x;
				this.x = nx;
				this._moveContainer(nx);
			}

		},

		_end: function(e) {
			if (!this.initiated) return;
			if (this.desktop || !this.options.menu) return; // if menu not applicable

			var point = hasTouch ? e.originalEvent.changedTouches[0] : e;
			var nx = parseInt(point.pageX) - this.ox;
			// choose direction based on dx
			if (this.dx <= 0) {
				this._animateTo(nx, 0);
			} else {
				this._animateTo(nx, this.options.menuWidth);
			}
			// open button
			if (this.dx === 0 && nx === 0 && this.tgt.is('.open')) {
				this._animateTo(this.options.menuWidth, this.options.menuWidth);
			}

			this.ox = null;
			this.dx = 0;
			this.initiated = false;

		},

		_animateTo: function(x,to){
			container.css({
				'transition-duration' : Math.floor(100 * x / this.snapThreshold) + 'ms',
				'transform' : 'translate(' + to + 'px,0)' + translateZ
			});
			// hide / show cover
			this._toggleCover(to);
		},

		_moveContainer: function(x){
			//container.style[transform] = 'translate(' + x + 'px,0)' + translateZ;
			container.css({
				'transform' : 'translate(' + x + 'px,0)' + translateZ
			})
		},

		_toggleCover: function(to){
			if (to > this.options.menuWidth - 50) {
				cover.show();
			} else {
				cover.hide();
			}
		}

	};

	/**
	* Feature Tests
	*/

	// test for touch deveices - from Modernizr
	function testTouch(){
		var bool = false;
		if(('ontouchstart' in window) || window.DocumentTouch && document instanceof DocumentTouch) {
			bool = true;
			$('html').addClass('touch');
		} else {
			$('html').addClass('pointer');
		}
		return bool;
	}

	// if iOS figure out thee address bar height offset
	function testOffset(){
		var offset = 0;
		// if safari on ios or ipod but not chrome
		if (navigator.userAgent.match(/(iPhone|iPod)/i)) {
			if (navigator.userAgent.indexOf('Safari') != -1 && navigator.userAgent.indexOf('CriOS') == -1) {
				offset = 60;
			}
		}
		// if in safari fullscreen mode
		if(("standalone" in window.navigator) && window.navigator.standalone){
			offset = 0;
		}
		return offset;
	}

	// 3d check
	function has3d() {
	    var el = document.createElement('p'),
	        has3d,
	        transforms = {
	            'webkitTransform':'-webkit-transform',
	            'OTransform':'-o-transform',
	            'msTransform':'-ms-transform',
	            'MozTransform':'-moz-transform',
	            'transform':'transform'
	        };
	    // Add it to the body to get the computed style.
	    document.body.insertBefore(el, null);
	    for (var t in transforms) {
	        if (el.style[t] !== undefined) {
	            el.style[t] = "translate3d(1px,1px,1px)";
	            has3d = window.getComputedStyle(el).getPropertyValue(transforms[t]);
	        }
	    }
	    document.body.removeChild(el);
	    return (has3d !== undefined && has3d.length > 0 && has3d !== "none");
	}

	return Bamboo;

})(window, document);
