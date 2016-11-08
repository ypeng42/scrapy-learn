<?php

   class PricePoint {
      var $date;
      var $price;
      var $promotion;
      var $shipping;

      function __construct($date, $price, $promotion, $shipping) {
         $this->date = $date;
         $this->price = $price;
         $this->promotion = $promotion;
         $this->shipping = $shipping;
      }
   }

   $product = $_POST["product_name"];
   $retailer = $_POST["retailer"];
   $brand = $_POST['brand'];

   // $product = "Huggies Little Movers Diaper Pants for Girls Size 5 (60 Count)";
   // $retailer = "Target";
   // $brand = "Huggies";

   $host        = "host=127.0.0.1";
   $port        = "port=5432";
   $dbname      = "dbname=test1";
   $credentials = "user=postgres password=123";

   $conn = pg_connect( "$host $port $dbname $credentials"  );

   if (!$conn) {
      echo "error";
   }

   // Get average price of all products from the brand
   $price_total = 0;
   $count = 0;
   $result = pg_query($conn, "SELECT current_price FROM product_info WHERE brand = '$brand'");
   
   while ($row = pg_fetch_assoc($result)) {
      $price_str = $row['current_price'];
      if (is_numeric($price_str)) {
          $count++;
          $price_total += floatval($price_str);
      }
   }

   $ave_price = number_format($price_total / $count, 2, '.', ',');


   // Get price over date
   $result = pg_query($conn, "SELECT * FROM product_price_info WHERE product_name = '$product'
      AND retailer = '$retailer'");

   $date_arr = array();
   $price_arr = array();
   $promo_arr = array();
   $shipping_arr = array();

   while ($row = pg_fetch_assoc($result)) {
      array_push($date_arr, $row['date_crawled']);
      array_push($price_arr, $row['current_price']);
      array_push($promo_arr, $row['promotion']);
      array_push($shipping_arr, $row['shipping']);
   }

   $current_date = array_shift($date_arr);

   $end_date = date('Y-m-d', time());

   $price = array_shift($price_arr);
   $promotion = array_shift($promo_arr);
   $promotion = empty($promotion) ? "N/A" : $promotion;

   $shipping = array_shift($shipping_arr);
   $shipping = empty($shipping) ? "N/A" : $shipping;

   $output = array();

   while (strtotime($current_date) <= strtotime($end_date)) {
      array_push($output, new PricePoint($current_date, $price, $promotion, $shipping));

      $current_date = date("Y-m-d", strtotime("+1 day", strtotime($current_date)));
      if (!empty($date_arr) && $current_date == $date_arr[0]) {
         array_shift($date_arr);
         $price = array_shift($price_arr);
         $promotion = array_shift($promo_arr);
         $promotion = empty($promotion) ? "N/A" : $promotion;

         $shipping = array_shift($shipping_arr);
         $shipping = empty($shipping) ? "N/A" : $shipping;
      }
   }

   echo json_encode((object) ['price_array' => $output, 'ave_price' => $ave_price]);
?>