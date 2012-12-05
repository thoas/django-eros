(function() {
  // Localize jQuery variable
  var jQuery;

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
    var like_url;

    jQuery(document).ready(function($) {
      $('.eros-button').each(function() {
        var _this = $(this),
            parent = _this.parent(),
            querystring = '?ctype=' + _this.data('ctype') + '&object_pk=' + _this.data('object-id');

          like_url = _this.data('like-url');

          _this.replaceWith('<iframe scrolling="no" frameborder="no" style="' + _this.attr('style') + '" src="' + like_url + querystring + '"></iframe>');
      });

      pm.bind('counter', function(data) {
        var url = data.url,
            el = $('#like-list-container');

        if (!el.length || el.attr('src') != url) {
          $(document.body).append('<iframe scrolling="no" frameborder="no" style="border: none; overflow: hidden; position: absolute; z-index: 1; display: none;" src="'+ data.url +'" id="like-list-container"></iframe>');

          var iframe = $('iframe[src="' + data.from_url + '"]');

          $('#like-list-container').load(function() {
            $(this).offset(iframe.offset());
          });
        } else {
          el.remove();
        }
      });

      pm.bind('load', function(data) {
        var iframe = $('#like-list-container');

        iframe.width(data.width).height(data.height).show();

        var offset = iframe.offset();
        offset.top -= data.height;

        iframe.offset(offset);
      });
    });
  }
})();
