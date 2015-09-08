(function($){
  $(function(){

  	var window_width = $(window).width();
  	if (window_width > 800){
  		var menu_width = window_width*0.5;
  	}else{
  		var menu_width = window_width*0.8;
  	};

    $('.button-collapse').sideNav({
      menuWidth: menu_width, // Default is 240
      edge: 'left', // Choose the horizontal origin
      closeOnClick: true // Closes side-nav on <a> clicks, useful for Angular/Meteor
    });
    $('.tooltipped').tooltip({delay: 50});
    $('select').material_select();

  }); // end of document ready
})(jQuery); // end of jQuery name space