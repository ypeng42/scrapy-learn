<html>
<head>
   <meta charset="UTF-8">
   
   <link rel="stylesheet" type = "text/css" href="css/makeup.css"/>
   <script src="//code.jquery.com/jquery-1.12.0.min.js"></script>
   <script src="//d3js.org/d3.v3.min.js" charset="utf-8"></script>
   <script src = "app.js?n=2"></script>
</head>


<body>

<?php
   $host        = "host=127.0.0.1";
   $port        = "port=5432";
   $dbname      = "dbname=test1";
   $credentials = "user=postgres password=maxpoint!db";


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


<div id = "retailer_pick_div" style="display: none;">
   <br/>
   Pick a retailer:  <select id='retailer_pick'> 
                        <option disabled selected value> -- select an option -- </option>
                        <option value="Walmart">Walmart</option>
                        <option value="Target">Target</option>
                        <option value="Walgreens">Walgreens</option>
                        <option value="Sams Club">Sams Club</option>
                        <option value="CVS">CVS</option>
                        <option value="Dollar General">Dollar General</option>
                     </select>

   <button type="button" class="show_hide" style="display: none;">Show/Hide Products</button>
   <button type="button" class="submit_button" style="display: none;">See Result</button>

   <div id="filter" style="display: none;">
      <br/>
      first filter term: <input type="text" id="filter_num" style="width: 70px;">
      second filter term: <input type="text" id="filter_unit" style="width: 70px;">
   </div>
   <br/>

</div>


<div id = "choose_product" style="display: none;" >

</div>


<div>
   <button type="button" class="submit_button" style="display: none;">See Result</button>
   <button type="button" class="show_hide" style="display: none;">Show/Hide All Checkboxes</button>
</div>


<div style="float: left;">
   <svg id="across_brand"></svg>
</div>

<div style="margin-top: 160px;">
   <table border="1" id="product_table" cellpadding="10" style="display: none;">
   
   </table>
</div>

</body>
</html>

