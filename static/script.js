import Tags from "/static/tags.js";
let server_side_tags = []
Tags.init("select:not(.ignore-tags)", {
  clearLabel: "Clear tag",
  allowClear: true,
  suggestionThresold: 0,
});
(function () {
  "use strict";

  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  const forms = document.querySelectorAll(".needs-validation");

  // Loop over them and prevent submission
  Array.prototype.slice.call(forms).forEach(function (form) {
    form.addEventListener(
      "submit",
      function (event) {
        // apply/remove invalid class
        // Array.from(form.elements).forEach(el => {
        //   console.log(el, el.checkValidity());
        // });

        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }

        form.classList.add("was-validated");
      },
      false
    );
  });
})();

export{server_side_tags}


