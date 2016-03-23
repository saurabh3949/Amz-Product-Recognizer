var getResults = function() {
    $("#submit_button").button("loading");
    $.post("/geturl", {
            url: $("#url").val()
        },
        function(data, status) {
            // alert(data);
            var imageURL = $("#url").val();
            var object = jQuery.parseJSON(data);
//            var cloth = object[0];
  //          var color = object[1];
            var i = 1;
            var all_objects = ""
            $.each(object, function(key,value) {
                all_objects += "<p>" + value + "</p>";
            });
        //    var i = 1;
        //    var all_captions = ""
        //    $.each(color, function(key,value) {
         //       all_captions += "<p>" + value + "</p>";
         //   });
            $("#objects")[0].innerHTML = all_objects;
        //    $("#captions")[0].innerHTML = all_captions;

            $("#submit_button").button('reset');
            $("#results-row").removeClass("hidden");
            $("#image-placeholder").attr("src", imageURL);

            // alert("Data: " + data + "\nStatus: " + status);
        }).error(function() {
        $("#results-row").addClass("hidden")
        $("#error").append('<div class="alert alert-info" id="error">Ooops! There was some problem in downloading that image. Please try using a URL with a jpg extension! <a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a></div>');
        $("#submit_button").button('reset');

    });
};

$(document).ready(function() {
    $('.bxslider').bxSlider({
  minSlides: 2,
  maxSlides: 2,
  slideWidth: 200,
  slideMargin: 10,
  // ticker: true,
  // speed: 10000
});

    $("#url").keypress(function(e) {
        if (e.which == 13) {
            getResults();
        }
    });


    $(".sample").click(function(){
        var url = $(this).attr("src");
        $("#url").val(url);
        getResults();


    });

    $("#submit_button").click(getResults);


});
