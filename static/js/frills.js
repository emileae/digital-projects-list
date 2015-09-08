




var sa = Snap("#svg-wwd");

var rect = null;
var screen_rect_1 = null;
var screen_rect_2 = null;
var screen_rect_3 = null;
var s1 = null;
var s2 = null;
var g0 = null;
var g1 = null;
var g2 = null;
var g3 = null;
var g4 = null;
var g5 = null;

var text = null;



function animate_text(word, x, y){
  if(text){
    //text.remove();
    text.attr({
      text: word
    });
    text.animate({
      x: x,
      y: y,
    }, 800, mina.elastic);
  }else{
    text = sa.text(x, y, word);
  };
  console.log(text);
  //text = sa.text(100, 200, word);
};



function service_animation(){
  if( screen_rect_1 ){
    screen_rect_1.remove();
  };
  if( screen_rect_2 ){
    screen_rect_3.remove();
  };
  if( screen_rect_3 ){
    screen_rect_3.remove();
  };
  if (rect){
    rect.remove();
  };
  if (s1){
    s1.remove();
  };
  if (s2){
    s2.remove();
  };
  if (g0){
    g0.remove();
  };
  if (g1){
    g1.remove();
  };
  if (g2){
    g2.remove();
  };
  if (g3){
    g3.remove();
  };
  if (g4){
    g4.remove();
  };
  if (g5){
    g5.remove();
  };

  var p1 = sa.path("M0 0L8 8ZM8 0L0 8Z").attr({
        fill: "#403c3f",
        stroke: "#1e292d",
        strokeWidth: 5
    });
  p1 = p1.pattern(0, 0, 8, 8);
  /*var p2 = sa.path("M0 5L5 0ZM6 4L4 6ZM-1 1L1 -1Z").attr({
        fill: "none",
        stroke: "#f2efef",
        strokeWidth: 5
    });
  p2 = p2.pattern(0, 0, 8, 8);*/

  rect = sa.rect(10, 10, 300, 200, 10, 10);

  rect.attr({
      fill: "none"
  });

  rect.attr({
      stroke: "#000",
      strokeWidth: 3,
  });

  //screen_rect_1 = sa.rect(-280, 20, 280, 20, 2, 2);
  screen_rect_1 = sa.rect(-280, 20, 280, 140, 2, 2);
  screen_rect_1.attr({
      fill: "none",
      stroke: "#000",
      strokeWidth: 3,
  });

  screen_rect_1.animate({
        x: 20,
        y: 20,
    }, 1000, mina.elastic);

  /*screen_rect_2 = sa.rect(600, 60, 280, 100, 2, 2);
  screen_rect_2.attr({
      fill: "none",
      stroke: "#000",
      strokeWidth: 2,
  });*/

  screen_rect_2 = sa.rect(144, 270, 30, 30, 10, 10);
  screen_rect_2.attr({
      fill: "none",
      stroke: "#000",
      strokeWidth: 3,
  });

  screen_rect_3 = sa.rect(110, 212, 100, 20);
  screen_rect_3.attr({
      fill: "none",
      stroke: "#000",
      strokeWidth: 3,
  });

  setTimeout(function(){

    screen_rect_3.animate({
          y: 400,
    }, 800, mina.elastic, function(){
      screen_rect_3.remove();
    });

  }, 1800);

  /*screen_rect_2.animate({
        x: 20,
        y: 60,
    }, 1000, mina.elastic);*/
  screen_rect_2.animate({
        x: 140,
        y: 170,
  }, 1000, mina.elastic);

  /*s1 = sa.rect(11, 11, 297, 197, 10, 10);
  s1.attr({
      stroke: "none",
      strokeWidth: 0,
  });*/

  /*var rect2 = sa.rect(15, 15, 290, 160, 10, 10);
  rect2.attr({
      fill: "#fff",
  });*/

  animate_text("WEB", 140, 270);

  /* WEB */
  setTimeout(function(){

    rect.animate({
        x: 112.5,
        y: 35,
        width: 75,
        height: 150
    }, 1200, mina.elastic);

    screen_rect_1.animate({
        x: 118.5,
        y: 42,
        width: 62,
        height: 116
    }, 1200, mina.elastic);

    screen_rect_2.animate({
        x: 144,
        y: 170,
        width: 10,
        height: 10,
        rx: 10,
        ry: 10,
    }, 1200, mina.elastic);

    /*s1.animate({
      opacity: 0
    }, 200);*/

    /*rect2.animate({
        width: 65,
        height: 140
    }, 1100, mina.elastic);*/

    animate_text("MOBILE", 120, 270);

    /* Mobile */
    setTimeout(function(){

      rect.animate({
          y: 60,
          x: 120,
          width: 50,
          height: 50,
          rx: 50,
          ry: 50,
      }, 1200, mina.elastic);

      setTimeout(function(){

        screen_rect_1.animate({
          opacity: 0
        }, 200);
        screen_rect_2.animate({
          opacity: 0
        }, 200);

      }, 100);

      /*rect2.animate({
          width: 0,
          height: 0,
          opacity: 0,
      }, 200);*/

      animate_text("GAMES", 130, 270);

      /* Games */
      setTimeout(function(){

        g0 = sa.rect(310, 200, 40, 20);
        g0.attr({
            fill: "none",
            stroke: "#000",
            strokeWidth: 3,
        });

        g0.animate({
          x: -80
        }, 1500);

        g1 = sa.rect(310, 0, 40, 100);
        g1.attr({
            fill: "none",
            stroke: "#000",
            strokeWidth: 3,
        });

        g1.animate({
          x: -80
        }, 1500);

        setTimeout(function(){

          g2 = sa.rect(310, 160, 40, 60);
          g2.attr({
              fill: "none",
              stroke: "#000",
              strokeWidth: 3,
          });

          g2.animate({
            x: -80
          }, 1500);

        }, 800);

        setTimeout(function(){

          g3 = sa.rect(310, 0, 40, 40);
          g3.attr({
              fill: "none",
              stroke: "#000",
              strokeWidth: 3,
          });
          
          g3.animate({
            x: -80
          }, 1500);

        }, 800);

        setTimeout(function(){

          g4 = sa.rect(310, 150, 40, 70);
          g4.attr({
              fill: "none",
              stroke: "#000",
              strokeWidth: 3,
          });
          
          g4.animate({
            x: -80
          }, 1500);

        }, 1300);

        setTimeout(function(){

          g5 = sa.rect(310, 0, 40, 50);
          g5.attr({
              fill: "none",
              stroke: "#000",
              strokeWidth: 3,
          });
          
          g5.animate({
            x: -80
          }, 1500);

        }, 1300);



        rect.animate({
            y: 140,
        }, 800, mina.easeinout, function(){

          rect.animate({
              y: 50,
          }, 800, mina.easeinout, function(){

            rect.animate({
                y: 80,
            }, 500, mina.easeinout, function(){

              //rect.animate({
              //    y: 150,
              //}, 500, mina.easeinout, function(){
                service_animation();
              //});
            });
          });
        });

      }, 500);

    }, 2000);

  }, 2000);
};

service_animation();


/* ---------- fishes ------------ */

//create fishes

//var ww = $(window).width();
var ww = $("#fish-container").width();

/*if (ww <= 320){
  num_fish = 10;
} else if ( ww <= 768 && ww > 320 ){
  num_fish = 20;
}else if ( ww > 768 ){
  num_fish = 67;
};*/
var num_fish = 3*(Math.floor(ww/85));

console.log("dimensions: ", ww+'--'+num_fish)

for ( var i=0; i< num_fish; i++ ){
  $("#fish-container").append('<svg id="f'+i+'" class="fish-svg"></svg>');
};


var fishes = $(".fish-svg");
      var unique_fish = Math.floor(Math.random()*num_fish);
      for(var i=0; i<fishes.length; i++){
        console.log(fishes[i].id);
        var s = Snap("#"+fishes[i].id);
        /*s.attr({
          opacity: 0.5
        });*/
        if(fishes[i].id == 'f'+unique_fish){
          load_svg(s, true)
        }else{
          load_svg(s, false);
        };
      };

      /*var s1 = Snap(".fish-svg1");
      load_svg(s1)
      var s2 = Snap(".fish-svg2");
      load_svg(s2)*/

      function load_svg(el, unique){
        if(!unique){
          var file_name = "small-fish-pad";
          //var file_name = "fish1";
        }else{
          var file_name = "small-fish-pad-hollow";
        };
        Snap.load("/static/img/"+file_name+".svg", function (f) {
            if( !unique ){
              f.selectAll("path[fill='#262262']").attr({fill: "#090248"});
              f.selectAll("polygon[fill='#262262']").attr({fill: "#090248"});
              var timing = 150;
            }else{
              f.selectAll("path[fill='#262262']").attr({fill: "#e70000"});
              f.selectAll("polygon[fill='#262262']").attr({fill: "#e70000"});
              var timing = 100;
            }
            /*f.selectAll("path[fill='#262262']").attr({fill: "#090248"});
            f.selectAll("polygon[fill='#262262']").attr({fill: "#090248"});*/
            var g = f.select("g");
            el.append(g);

            var bbox = g.getBBox();

            if(!unique){
              var cx = bbox.cx;
            }else{
              var cx = bbox.cx+20;
            };

            function easeinout_rotate(deg, time, callback){
              g.animate( { transform: "r" + deg + ","+cx+","+bbox.cy+"" }, time, mina.easeinout, callback );
              /*el.animate({
                opacity: 1
              }, time);*/
            };

            function fish_tail(){
              easeinout_rotate(15, timing, function(){
                easeinout_rotate(-15, 2*timing, function(){
                  easeinout_rotate(0, timing, null);
                });
              });

              /*el.animate({
                opacity: 0.5
              }, 2000);*/
            };

            g.mouseover(function(){
              fish_tail();
            });

            $("body").on("click", "#fish-container", function(){
              fish_tail();
            });

        });
      };


