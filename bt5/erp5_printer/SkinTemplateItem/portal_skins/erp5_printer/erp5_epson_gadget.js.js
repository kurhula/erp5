/*global window, rJS, document*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, document) {
  "use strict";
  var gadget_klass = rJS(window);

  gadget_klass
    .declareAcquiredMethod("submitContent", "submitContent")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("redirect", "redirect")


    .declareMethod("render", function (options) {
      var gadget = this;
      gadget.state.jio_key = options.jio_key;
      return gadget.getSetting('hateoas_url')
       .push(function (hateoas_url) {
          gadget.state.hateoas_url = hateoas_url;
        });
    })
    .onEvent('submit', function submit(options) {
      var method = document.activeElement.value,
       gadget = this;
      return gadget.submitContent(
        gadget.state.jio_key,
        gadget.state.hateoas_url + gadget.state.jio_key + "/" + method,
        {})
        .push(function (result) {
          return gadget.redirect({
              command: 'display',
              options: {
                "jio_key": result.jio_key,
                "view": result.view
              }
            });
        })
        .push(undefined, function(error) {
          if (! error instanceof RSVP.CancellationError) {
            throw error
          }
        });
    });
}(window, rJS, document));
