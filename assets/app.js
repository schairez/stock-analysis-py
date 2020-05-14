$("li")
  .mouseover(function () {
    $(this).find(".drop-down").slideDown(300);
    $(this).find(".accent").addClass("animate");
    $(this).find(".item").css("color", "#FFF");
  })
  .mouseleave(function () {
    $(this).find(".drop-down").slideUp(300);
    $(this).find(".accent").removeClass("animate");
    $(this).find(".item").css("color", "#000");
  });
