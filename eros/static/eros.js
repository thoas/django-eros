(function() {
  // Localize jQuery variable
  var jQuery;

  var template = '<div class="eros-button-container"> \
    <a class="eros-button-like btn" href="<%= like_url %>"><%= label %></a> \
    &nbsp; \
    <a href="<%= list_url %>" class="eros-counter"> \
        <span class="eros-counter-label"><%= count %></span> \
    </a> \
</div>';

  // see: http://ejohn.org/blog/javascript-micro-templating/
  this.tmpl = function tmpl(str, data){
    // Figure out if we're getting a template, or if we need to
    // load the template - and be sure to cache the result.
    var fn = !/\W/.test(str) ?
      cache[str] = cache[str] ||
        tmpl(document.getElementById(str).innerHTML) :

      // Generate a reusable function that will serve as a template
      // generator (and which will be cached).
      new Function("obj",
        "var p=[],print=function(){p.push.apply(p,arguments);};" +

        // Introduce the data as local variables using with(){}
        "with(obj){p.push('" +

        // Convert the template into pure JavaScript
        str
          .replace(/[\r\t\n]/g, " ")
          .split("<%").join("\t")
          .replace(/((^|%>)[^\t]*)'/g, "$1\r")
          .replace(/\t=(.*?)%>/g, "',$1,'")
          .split("\t").join("');")
          .split("%>").join("p.push('")
          .split("\r").join("\\'")
      + "');}return p.join('');");

    // Provide some basic currying to the user
    return data ? fn( data ) : fn;
  };

  // see: http://alexmarandon.com/articles/web_widget_jquery/
  if (window.jQuery === undefined || window.jQuery.fn.jquery !== '1.8.3') {
      var script_tag = document.createElement('script');
      script_tag.setAttribute('type','text/javascript');
      script_tag.setAttribute('src',
          'http://ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js');
      if (script_tag.readyState) {
        script_tag.onreadystatechange = function () { // For old versions of IE
            if (this.readyState == 'complete' || this.readyState == 'loaded') {
                scriptLoadHandler();
            }
        };
      } else {
        script_tag.onload = scriptLoadHandler;
      }
      // Try to find the head, otherwise default to the documentElement
      (document.getElementsByTagName('head')[0] || document.documentElement).appendChild(script_tag);
  } else {
      // The jQuery version on the window is the one we want to use
      jQuery = window.jQuery;
      main();
  }

  function scriptLoadHandler() {
      jQuery = window.jQuery.noConflict(true);
      main();
  }

  function main() {
      jQuery(document).ready(function($) {
        $('.eros-button').each(function() {
          var _this = $(this),
              parent = _this.parent(),
              like_url = _this.data('like-url'),
              like_list_url = _this.data('like-list-url'),
              querystring = '?ctype=' + _this.data('ctype') + '&object_pk=' + _this.data('object-id') + '&callback=?';

            $.getJSON(like_url + querystring, function(data) {
              _this.replaceWith(tmpl($('#eros-template').html() || template, {
                like_url: like_url + querystring + '&submit=1',
                list_url: like_list_url,
                count: data.count,
                label: _this.html()
              }));

              parent.find('.eros-button-like').click(function(e) {
                e.preventDefault();

                var elem = $(this);

                $.getJSON(elem.attr('href'), function(data) {
                  parent.find('.eros-counter-label').html(data.count);
                  elem.toggleClass('liked');
                });
              });
            });
        });
      });
  }
})();
