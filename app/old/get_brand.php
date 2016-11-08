<?php 
   $category = $_POST["category"];
   
   $host        = "host=127.0.0.1";
   $port        = "port=5432";
   $dbname      = "dbname=test1";
   $credentials = "user=postgres password=123";

   $conn = pg_connect( "$host $port $dbname $credentials"  );

   if (!$conn) {
      echo "error";
   } 

   $output = array();
   $result = pg_query($conn, "SELECT brand FROM brandlist WHERE category = '$category'");

   while ($row = pg_fetch_assoc($result)) {
      array_push($output, $row['brand']);
   }

   echo json_encode($output);
?>