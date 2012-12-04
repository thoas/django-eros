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

          like_url = _this.data('like-url'),

          _this.replaceWith('<iframe scrolling="no" style="' + _this.attr('style') + '" src="' + like_url + querystring + '"></iframe>');
      });

      $('iframe').each(function() {
        $(this).load(function() {
          var iframe = $(this);
          $(this).contents().find('a.eros-counter').click(function(e) {

            $(document.body).append('<iframe scrolling="no" style="border: none; overflow: hidden; position: absolute; z-index: 1; display: none;" src="'+ $(this).attr('href') +'" id="like-list-container"></iframe>')

            $('#like-list-container').load(function() {
              $(this).height($(this).contents().find("html").height());
              $(this).width($(this).contents().find("html").width());

              $(this).offset(iframe.offset()).show();
            });
          });
        });
      });
    });
  }
})();
