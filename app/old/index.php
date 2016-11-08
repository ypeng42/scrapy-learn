<html>
<head>
   <meta charset="UTF-8">
   
   <link rel="stylesheet" type = "text/css" href="css/makeup.css"/>
   <link rel="shortcut icon" type="image/x-icon"  href="favicon.ico">
   <script src="//code.jquery.com/jquery-1.12.0.min.js"></script>
   <script src="//d3js.org/d3.v3.min.js" charset="utf-8"></script>
   <script src = "app.js"></script>
</head>


<body>

<?php
   $host        = "host=127.0.0.1";
   $port        = "port=5432";
   $dbname      = "dbname=test1";
   $credentials = "user=postgres password=123";

   $conn = pg_connect( "$host $port $dbname $credentials"  );

   if (!$conn) {
      echo "Error : Unable to open database\n";
   } 

   echo "Pick a category:   <select id='category_pick'>";
   echo "<option disabled selected value> -- select an option -- </option>";

   $result = pg_query($conn, "SELECT DISTINCT category FROM brandlist");

   while ($row = pg_fetch_assoc($result)) {
      echo '<option value="'.$row['category'].'">'.$row['category'].'</option>';
   }

   echo "</select>";
   echo "<br/>";
?>


<div id = "brand_div" style="display: none;">
<br/>
Pick a brand:  <select id='brand_pick'> </select>
</div>


<div id = "product_div" style="display: none;">
<br/>
Pick a Product:  <select id='product_pick'> </select>
</div>
   

<div id = "search_competitors" style="display: none;">
   <br/>
   Find competitors Across: 
   <select id = "brand_or_retail">
      <option value = "retailer"> retailer </option>
      <option value = "brand"> brand </option>
   </select>
   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
   <button type = "button" id = "search_btn"> Search </button>
</div>


<div id = "pick_competitor" style="display: none;">
   <br/>
   Pick a competing product:  <select id='competitor_pick'> </select>
</div>


<div id = "picked_product_info_div">

</div>

<div id = "picked_competitor_info_div">

</div>

<svg id="origin_vis" width="600" height="350"></svg>
<svg id="competitor_vis" width="600" height="350"></svg>

</body>
</html>

