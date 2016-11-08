
$(document).ready(function(){

function is_brand(str) {
  arr = str.split(" ");
  is_b = true;
  for (i = 0; i < arr.length; i++) {
    if (arr[i][0] !== arr[i][0].toUpperCase()) {
      is_b = false;
    }
  }
  return is_b;
}


function show_buttons() {
  $('.show_hide').show();
  $('.submit_button').show();
}

function hide_buttons() {
  $('.show_hide').hide();
  $('.submit_button').hide();
}

function clear_text_fields(){
  $('#filter_unit').val("");
  $('#filter_num').val("");
}


function build_checkbox(filter_num, filter_unit) {
    $.each(checkboxes_list, function(key, value) {
        $wrapper = $("<div class='cb_wrapper'>");
        // $wrapper.html('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<h3>' + key + "</h3><br/>");

        $ul = $("<ul>");
        $ul.append('<h3>' + key + "</h3>");

        $.each(value, function(index, obj) {
            if (obj.product_name.toLowerCase().indexOf(filter_num) != -1
              && obj.product_name.toLowerCase().indexOf(filter_unit) != -1) {
                $ul.append(
                    "<li><input type='checkbox' value='" + obj.product_name + "'/>" +
                    '<a href="' + obj.url + '">' + obj.product_name + "</a><br/>" +
                    "<img src = " + obj.img_url + " alt = 'Product Image'" + 
                    " style=width:150px;height:100px;>" +

                    "</li>"
                );
            }
        })

        $ul.appendTo($wrapper);

        $wrapper.appendTo('#choose_product');
    });

    // Adjust the length of each column according to number of retailers
    retailer_num = Object.keys(checkboxes_list).length;
    $(".cb_wrapper").css("width", 100 / retailer_num + "%");

    // Add a clear div to offset "float: left" 
    $('#choose_product').append("<div class='clear'></div>");
}



class PriceInfo {
  constructor(name, average, variance) {
    this.name = name;
    this.average = average;
    this.variance = variance;
  }

  setScore(score) {
    this.score = score;
  }
}

curr_retailer = "";
checkboxes_list = {};
plist = [];


price_across_brand = [];

brand = [];

// Pick a category
$("#category_pick").on('change', function() {
    brand = [];

    checkboxes_list = {};

    // Hide table, clear graph
    $("#across_brand").empty();
    $('#product_table').hide();
    
    // Hide checkboxes and buttons
    $("#choose_product").hide();
    $('#filter').hide();
    hide_buttons();

    $("#retailer_pick_div").show();

    // Back to default select
    $('#retailer_pick>option:eq(0)').prop('selected', true);

    $.ajax({
      url: 'get_brand.php',
      type: 'post',
      data: {'category' : this.value},
      dataType: "json",

      success: function(data) {

        $.each(data, function(index, value) {
            brand.push(value);
        });

      },

      error: function(exception) {
        alert(exception);
      }

    }); 
});



$("#retailer_pick").on('change', function() {

    show_buttons();
    clear_text_fields();
    $('#filter').show();

    // Hide table, clear graph
    $("#across_brand").empty();
    $('#product_table').hide();

    checkboxes_list = {};

    curr_retailer = this.value;

    // show checkboxes
    $("#choose_product").empty();
    $("#choose_product").show();
    
    // Get a list of products
    $.ajax({
        url: 'get_product_from_term.php',
        type: 'post',
        data: {"search_terms": brand, "retailer" : this.value},
        dataType: "json",

        success: function(data) {

          $.each(data, function(index, value) {
              if (!(value.search_term in checkboxes_list)) {
                  checkboxes_list[value.search_term] = [];
                  checkboxes_list[value.search_term].push({
                      "product_name" : value.product_name,
                      "img_url" : value.img_url,
                      "url" : value.url,
                      "search_term": value.search_term
                  });
              } else {
                  checkboxes_list[value.search_term].push({
                      "product_name" : value.product_name,
                      "img_url" : value.img_url,
                      "url" : value.url,
                      "search_term": value.search_term
                  });
              }

          });

          build_checkbox("", "");

        },

        error: function(exception) {
          alert(exception);
        }

    }); 
});



$('body').on('keyup paste', '#filter_num', function () {
    $("#choose_product").empty();
    build_checkbox($('#filter_num').val().toLowerCase(), $('#filter_unit').val().toLowerCase());
});

$('body').on('keyup paste', '#filter_unit', function () {
    $("#choose_product").empty();
    build_checkbox($('#filter_num').val().toLowerCase(), $('#filter_unit').val().toLowerCase());
});



// Get pricing info for all the products picked
$('body').on('click', '.submit_button', function () {
    // Clear and rebuild the plist
    var plist = [];
    var price_across_brand = [];

    $("#across_brand").empty();

    $('#product_table').show();
    $('#product_table').empty();

    $(':checkbox:checked').each(function(i){
          plist[i] = $(this).val();
    });

    $.ajax({
        url: 'get_price.php',
        type: 'post',
        data: {'plist' : plist, "search_list" : Object.keys(checkboxes_list), 
                "retailer" : curr_retailer},
        dataType: "json",

        success: function(data) { 
          $.each(data['price_info'], function(index, value) {
              if (value.average != 0) {
                price_across_brand.push(new PriceInfo(value.search_term, value.average,
                  value.variance));
              }
          });

          show_price(price_across_brand, "#across_brand");

          // Create product table
          $('#product_table').append("<tr><td> Product</td>" +
              "<td> Search Term</td>" +
              "<td> Average Price</td>" +
              "<td> Variance</td>" +
              "<td> Count</td>" +
              "<td> Volume</td>" +
              "<td> Pack</td>" +
              "</tr>"
          );

          $.each(data['product_info'], function(index, value) {
              $('#product_table').append(
                  "<tr>" +
                  "<td>" + '<a href="' + value.url + '">' + 
                  value.product_name + "</a></td>" +
                  
                  "<td>" + value.search_term + "</td>" +
                  "<td>$" + value.average_price.toFixed(2) + "</td>" +
                  "<td>$" + value.variance.toFixed(2) + "</td>" +
                  "<td>" + value.count_no + "</td>" +
                  "<td>" + value.volume_no + "</td>" +
                  "<td>" + value.pack_no + "</td>" +
                  "</tr>"
              );
          });

        },

        error: function(exception) {
          alert(exception);
        }

    }); 
});

// Show / Hide all the product and checkboxes
$('body').on('click', '.show_hide', function () {
    $("#choose_product").toggle();
});




























function customAxis(g) {
  g.selectAll("text")
      .attr("x", 4)
      .attr("dy", -4);
}


function show_price(data, id) {
    if (data.length == 0) {
      alert("No price info for this term");
      return;
    }

    var WIDTH = 800,
        HEIGHT = 550,
        MARGINS = {
            top: 50,
            right: 50,
            bottom: 50,
            left: 50
        },
          vis = d3.select(id)
                  .attr("width", WIDTH)
                  .attr("height", HEIGHT),

          xScale = d3.scale.ordinal()
                  .rangeRoundBands([MARGINS.left, WIDTH - MARGINS.right], 0.4)
                  .domain(data.map(function(d){
                      return d.name;
                   })),

          yScale = d3.scale.linear()
                  .range([HEIGHT - MARGINS.top, MARGINS.bottom])
                  .domain([0, d3.max(data, function(d) {
                      return d.average;
                   }) * 1.1]),


          xAxis = d3.svg.axis()
                  .scale(xScale)
                  .orient("bottom")
                  .tickSize(10),

          yAxis = d3.svg.axis()
                  .scale(yScale)
                  .tickSize(WIDTH)
                  .orient("right")
                  .ticks(10)
                  .tickFormat(function(d) { return d + "$"; } ),

          gy = vis.append("g")
              .attr("class", "y axis")
              .call(yAxis)
              .call(customAxis),

          tooltip = d3.select("body").append("div")
                    .attr("class", "tooltip")
                    .style("opacity", 0);

          vis.append("svg:g")
                  .attr("class","x axis")
                  .attr("transform", "translate(0," + (HEIGHT - MARGINS.bottom) + ")")
                  .call(xAxis);

          vis.append("svg:g")
                  .append("text")
                  .attr("y", 27)
                  .attr("x", 110)
                  .attr("font-size", "15px")
                  .style('fill', 'darkOrange')
                  .attr("dy", ".71em")
                  .style("text-anchor", "end")
                  .text("Average Price");


          vis.selectAll(".bar")
              .data(data)
              .enter()
              .append("rect")
              .attr("class", "bar")
              .attr("x", function(d) { return xScale(d.name); })
              .attr("width", xScale.rangeBand())
              .attr("y", HEIGHT - MARGINS.bottom)
              .attr("height", 0)
              .on("mouseover", function(d) {
                        tooltip.transition()
                             .duration(200)
                             .style("opacity", .9);

                        var str = d.name + "<br/>" +
                                  "price: $" + d.average.toFixed(2) + 
                                  "<br/> variance: $" + d.variance.toFixed(2);

                        tooltip.html(str)
                               .style("left", (d3.event.pageX + 5) + "px")
                               .style("top", (d3.event.pageY - 28) + "px");
                    })
              .on("mouseout", function(d) {
                  tooltip.transition()
                       .duration(500)
                       .style("opacity", 0);
                })
              .attr("fill", function(d) {
                  return "rgb(0, 0, " + d3.min([255, Math.round((d.average * 5))]) + ")";
               })
              .transition()
              .duration(1500)
              .attr("y", function(d) {return yScale(d.average); })
              .attr("height", function(d) {return HEIGHT - MARGINS.bottom - yScale(d.average); });   
}



});