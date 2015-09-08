$("body").on("submit", "#project_form", function(e){

  //var form = $(this); // You need to use standart javascript object here
  var formData = $( this ).serializeArray();

  e.preventDefault();

  function success(data){
    if ( data["message"] == "success" ){
      $("#message").html("Your project has been posted, thanks!");
      
      var $new_card = $(".project_card").first().clone();
      console.log($new_card);

      $new_card.attr("id", "project_"+data["project_id"]);

      $("#project_"+data["project_id"]).find(".project-link").html(data["title"]);
      $("#project_"+data["project_id"]).find(".project-link").attr("href", "/project/"+data["project_id"]);
      $("#project_"+data["project_id"]).find(".value").html(data["currency"]+" "+data["value"]);
      $("#project_"+data["project_id"]).find(".description").html(data["description"]);

      if ( $("#project_"+data["project_id"]).hasClass("hidden") ){
        $("#project_"+data["project_id"]).removeClass("hidden")
      };

      $('#project_form')[0].reset();
      setTimeout(function(){
        $('.button-collapse').sideNav('hide');
      }, 3000);
    }else{
      //$("#message").html("There was a problem posting your project");
      $("#message").html(data["long_message"]);
      if ( data["errors"] ){
        for (var i=0; i<data["errors"].length; i++){
          $("#"+data["errors"]).addClass("error");
        }
      }
    };
    $("#message").addClass("emphasis");
  };

  console.log("formData: ", formData);

  $.ajax({
      url: '/save_project',
      type: "post",
      data: formData,
      // THIS MUST BE DONE FOR FILE UPLOADING
      //contentType: false,
      //processData: false,
      success: success
  }).fail(function(err){
    $("#message").html("There was a problem posting your project, please try again later");
    console.log("error, ", err);
  });

});

$("body").on("submit", "#response-form", function(e){

  //var form = $(this); // You need to use standart javascript object here
  var formData = $( this ).serializeArray();
  var action = $( this ).attr("action");

  e.preventDefault();

  function success(data){
    if ( data["message"] == "success" ){
      $("#response-message").html(data["long_message"]);
      
      var $new_card = $(".response-card").first().clone();

      $new_card.attr("id", "response-"+data["response_id"]);
      $("#response-list").prepend( $new_card );
      $("#empty-content-note").html("");

      $("#response-"+data["response_id"]).find(".response-hook").html(data["hook"]);
      $("#response-"+data["response_id"]).find(".response-link").attr("href", data["website"]);

      if ( $("#response-"+data["response_id"]).hasClass("hidden") ){
        $("#response-"+data["response_id"]).removeClass("hidden")
      };

      $('#response-form')[0].reset();
      setTimeout(function(){
        $("#response-box").toggleClass("open");
      }, 3000);
    }else{
      $("#response-message").html(data["long_message"]);
      $("#response-form").find("input").removeClass("error");
      if ( data["errors"] ){
        for (var i=0; i<data["errors"].length; i++){
          $("#response-form").find("#"+data["errors"]).addClass("error");
        }
      }
    };

    $("#response-message").addClass("emphasis");
  };

  $.ajax({
      url: action,
      type: "post",
      data: formData,
      success: success
  }).fail(function(err){
    $("#response-message").html("There was a problem posting your response, please try again later");
    console.log("error, ", err);
  });

});



$("body").on("submit", "#contact_form", function(e){
  console.log("AJAX... hello");
  e.preventDefault();
  var name = $("#enquiry_name").val();
  var email = $("#enquiry_email").val();
  var description = $("#enquiry_description").val();

  function success(data){
    $("#enquiry_name").val("");
    $("#enquiry_email").val("");
    $("#enquiry_email").removeClass("valid");
    $("#enquiry_description").val("");

    $("#thank_you").css("height", "10rem");
  };

  $.ajax({
    url: "/contact",
    type: "post",
    data: {
      "enquiry_name": name, 
      "enquiry_email": email,
      "enquiry_description": description, 
    },
    success: success
  });

});

$("body").on("submit", "#mailing_list_form", function(e){
  
  e.preventDefault();
  var name = $("#subscriber_name").val();
  var email = $("#subscriber_email").val();

  function success(data){
    $("#subscriber_name").val("");
    $("#subscriber_email").val("");
    $("#subscriber_email").removeClass("valid");

    $("#thank_you_subscribe").css("height", "4rem");
  };

  $.ajax({
    url: "/subscribe",
    type: "post",
    data: {
      "name": name, 
      "email": email,
    },
    success: success
  });

});

$("body").on("submit", "#unsubscribe_form", function(e){
  
  e.preventDefault();
  var email = $("#subscriber_email").val();

  console.log("ajax 1");

  function success(data){
    console.log("ajax 2");
    $("#subscriber_email").val("");
    $("#subscriber_email").removeClass("valid");

    $("#thank_you_unsubscribe").css("height", "4rem");
  };

  $.ajax({
    url: "/unsubscribe",
    type: "post",
    data: {
      "email": email,
    },
    success: success
  });

});