
$(document).ready(function(){

class Product {
  constructor(product, retailer, img_url, url, brand, price) {
    this.product_name = product;
    this.retailer = retailer;
    this.img_url = img_url;
    this.url = url;
    this.brand = brand;
    this.price = price;
  }

  setScore(score) {
    this.score = score;
  }

}

var picked_product_list = [];
var competitor_list = [];
var curr_product;
var curr_competitor;


$("#category_pick").on('change', function() {
    // alert($(this).val());

    $('#brand_div').show();

    $('#brand_pick')
      .empty();

    $.ajax({
      url: 'get_brand.php',
      type: 'post',
      data: {'category' : this.value},
      dataType: "json",

      success: function(data) {
        $('#brand_pick')
            .prepend("<option disabled selected value> -- select an option -- </option>");

        $.each(data, function(key,value) {
            $('#brand_pick')
             .append($("<option></option>")
             .attr("value",value)
             .text(value)); 
        });
      },

      error: function(exception) {
        alert(exception);
      }

    }); 
});


$("#brand_pick").on('change', function() {

    $('#product_div').show();

    picked_product_list = [];

    $('#product_pick')
      .empty();


    $.ajax({
      url: 'get_product.php',
      type: 'post',
      data: {'brand' : this.value},
      dataType: "json",

      success: function(data) {
        $('#product_pick')
            .prepend("<option disabled selected value> -- select an option -- </option>");

        var i = 0;
        $.each(data, function(index, value) {
            picked_product_list.push(new Product(value.product_name, value.retailer, 
              value.img_url, value.url, value.brand, value.price));

            $('#product_pick')
             .append($("<option></option>")
             .attr("value", i)
             .text((i + 1) + ". " + value.product_name)); 

            i++;
        });
      },

      error: function(exception) {
        alert(exception);
      }

    }); 
});


$("#product_pick").on('change', function() {
    $("#search_competitors").show();
    $("#origin_vis").empty();

    var curr_index = $('#product_pick').find(":selected").val();
    curr_product = picked_product_list[curr_index]

    $("#picked_product_info_div").html(
      "<br/><br/><hr><br/>" +
      'Product Name: <a target="_blank" href = "' + curr_product.url + '">' + curr_product.product_name + "</a>" +
      "<br/> Retailer: " + curr_product.retailer + 
      "<br/> Price: " + curr_product.price +
      "<br/> Brand: " + curr_product.brand +
      '<br/><br/><button type = "button" id = "get_price_btn"> Show Price Change</button>' +
      "<br/><img src = " + curr_product.img_url + " alt = 'Product Image'" + 
      " style=width:200px;height:150px;>"
      );
});




$('body').on('click', '#get_price_btn', function () {

    if (!$.trim( $('#origin_vis').html() ).length) {

       $.ajax({
        url: 'get_price.php',
        type: 'post',
        data: {'product_name' : curr_product.product_name, 'retailer' : curr_product.retailer,
              'brand' : curr_product.brand},
        dataType: "json",

        success: function(data) {
          show_product_price(data['price_array'], "origin", "#origin_vis", data['ave_price']);
          // $.each(data, function(index, value) {
          //     alert(value.date);
          // });
        },

        error: function(exception) {
          alert(exception);
        }
   
       });
    } 
});


$('body').on('click', '#get_competitor_price_btn', function () {

    if (!$.trim( $('#competitor_vis').html() ).length) {
       $.ajax({
        url: 'get_price.php',
        type: 'post',
        data: {'product_name' : curr_competitor.product_name, 'retailer' : curr_competitor.retailer,
              'brand' : curr_product.brand},
        dataType: "json",

        success: function(data) {
          show_product_price(data['price_array'], "competitor", "#competitor_vis", data['ave_price']);
        },

        error: function(exception) {
          alert(exception);
        }

      }); 
    } 

});







$("#competitor_pick").on('change', function() {

    var curr_index = $('#competitor_pick').find(":selected").val();
    curr_competitor = competitor_list[curr_index]
    $("#competitor_vis").empty();

    $("#picked_competitor_info_div").html(
      "<br/><br/><hr><br/>" + 
      'Product Name: <a target="_blank" href = "' + curr_competitor.url + '">' + curr_competitor.product_name + "</a>" +
      "<br/> Retailer: " + curr_competitor.retailer + 
      "<br/> Price: " + curr_competitor.price +
      "<br/> Brand: " + curr_competitor.brand +
      "<br/> Similarity Score: " + curr_competitor.score.toFixed(2) + 
      '<br/><button type = "button" id = "get_competitor_price_btn"> Show Price Change</button>' +
      "<br/><br/><img src = " + curr_competitor.img_url + " alt = 'Product Image'" + 
      " style=width:200px;height:150px;>"
      );

    if (curr_competitor.price == -1) {
      $("#get_competitor_price_btn").remove();
    } 

});



$("#search_btn").on('click', function(){
    $("#pick_competitor").show();

    competitor_list = [];

    $('#competitor_pick')
      .empty();

    var choice = $('#brand_or_retail').find(":selected").val();

    $.ajax({
      url: 'search_competitors.php',
      type: 'post',
      data: {'product_name' : curr_product.product_name, 'retailer' : curr_product.retailer,
             'choice' : choice},
      dataType: "json",

      success: function(data) {
        $('#competitor_pick')
            .prepend("<option disabled selected value> -- select an option -- </option>");


        var i = 0;
        $.each(data, function(index, value) {
          prod = new Product(value.product_name, value.retailer, value.img_url, value.url,
            value.brand, value.price);
          prod.setScore(value.score);

          competitor_list.push(prod);

            $('#competitor_pick')
             .append($("<option></option>")
             .attr("value", i)
             .text((i+1) + ". " + value.product_name)); 

            i++;
        });

      },

      error: function(exception) {
        alert(exception);
      }

    }); 

});



function show_product_price(input, who, id, ave_price) {
    // alert(ave_price);
    var data = JSON.parse(JSON.stringify(input));

    var vis = d3.select(id),
        WIDTH = 600,
        HEIGHT = 350,
        MARGINS = {
            top: 50,
            right: 50,
            bottom: 50,
            left: 50
        },

        xScale = d3.time.scale()
            .range([MARGINS.left, WIDTH - MARGINS.right])
            .domain([new Date(data[0].date), 
                d3.time.day.offset(new Date(data[data.length - 1].date), 1)]),

        yScale = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom])
                .domain([0, Math.max(d3.max(data, function(d) {
                    return d.price;
                  }), ave_price) * 1.5]);


        // if (who == "origin") {
          // Append axis and text
          var xAxis = d3.svg.axis()
                  .scale(xScale)
                  .ticks(5)
                  .tickFormat(d3.time.format('%m/%d')),

          yAxis = d3.svg.axis()
                  .scale(yScale)
                  .orient("left");

          vis.append("svg:g")
                  .attr("class","axis")
                  .attr("transform", "translate(0," + (HEIGHT - MARGINS.bottom) + ")")
                  .call(xAxis);

          vis.append("svg:g")
                  .attr("class","axis")
                  .attr("transform", "translate(" + (MARGINS.left) + ",0)")
                  .call(yAxis);

          vis.append("text")
                .attr("transform", "translate("+ (MARGINS.left / 3) +","+(HEIGHT / 2)+")rotate(-90)")    
                .text("Price ($)");

          vis.append("text")
                .attr("text-anchor", "middle")  // this makes it easy to centre the text as the transform is applied to the anchor
                .attr("transform", "translate("+ (WIDTH/2) +","+(HEIGHT)+")")  // centre below axis
                .text("Date");
        // }

        var parseDate = d3.time.format("%Y-%m-%d").parse;

        var lineGen = d3.svg.line()
                    .x(function(d) {
                      return xScale(parseDate(d.date));
                    })
                    .y(function(d) {
                      return yScale(d.price);
                    });
                    // .interpolate("basis");

        var color = "green";

        if (who == "competitor") {
          color = "red";
        }

        var tooltip = d3.select("body").append("div")
                    .attr("class", "tooltip")
                    .style("opacity", 0);

        vis.selectAll("circle." + who)
                   .data(data)
                   .enter()
                   .append("circle")
                   .attr("class", who)
                   .attr("cx", function(d) {
                        return xScale(parseDate(d.date));
                    })
                   .attr("cy", function(d) {
                        return yScale(d.price);
                    })
                   .attr("fill", color)
                   .on("mouseover", function(d) {
                        tooltip.transition()
                             .duration(200)
                             .style("opacity", .9);

                        var str = "date: " + d.date + "<br/> price: $" + d.price;
                        if (d.promotion != "N/A") {
                              str += "<br/>promotion: " + d.promotion;
                        }

                        if (d.shipping != "N/A") {
                              str += "<br/>shipping: " + d.shipping;
                        }

                        tooltip.html(str)
                             .style("left", (d3.event.pageX + 5) + "px")
                             .style("top", (d3.event.pageY - 28) + "px");
                    })
                    .on("mouseout", function(d) {
                        tooltip.transition()
                             .duration(500)
                             .style("opacity", 0);
                    })
                   .transition()
                   .delay(function(d, i) { return i * (3000 / (data.length - 1)); })
                   .attr("r", 5);

      // Add legend
      var legend = vis.append("g")
                    .attr("class", "legend")
                    .attr("x", WIDTH - 75)
                    .attr("y", 35)
                    .attr("height", 150)
                    .attr("width", 150);

                  legend.append("circle")
                    .attr("cx", WIDTH - 100)
                    .attr("cy", 75)
                    .attr("r", 5)
                    .style("fill", color);

                  legend.append("text")
                    .attr("x", WIDTH - 85)
                    .attr("y", 80)
                    .text("Price Change");


      if (ave_price != -1) {
          legend.append("rect")
            .attr("x", WIDTH - 105)
            .attr("y", 45)
            .attr("width", 10)
            .attr("height", 10)
            .style("fill", "orange");

          legend.append("text")
            .attr("x", WIDTH - 85)
            .attr("y", 55)
            .text("Brand Average");

          vis.append('line')
                  .attr({x1 : xScale(parseDate(data[0].date)), y1 : yScale(ave_price),
                         x2 : xScale(parseDate(data[data.length - 1].date)), y2 : yScale(ave_price)})
                  .attr('stroke', "orange")
                  .attr("class", "ave")
                  .attr('stroke-width', 2)
                  .attr('fill', 'none');
      }

      var path = vis.append('svg:path')
                        .attr('d', lineGen(data))
                        .attr('stroke', color)
                        .attr("class", who)
                        .attr('stroke-width', 2)
                        .attr('fill', 'none');

      var totalLength = path.node().getTotalLength();

      path.attr("stroke-dasharray", totalLength + " " + totalLength)
          .attr("stroke-dashoffset", totalLength)
          .transition()
          .duration(3000)
          .ease("linear")
          .attr("stroke-dashoffset", 0);
}



});