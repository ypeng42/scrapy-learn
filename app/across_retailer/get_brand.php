<?php 
   $category = $_POST["category"];
   
   $host        = "host=127.0.0.1";
   $port        = "port=5432";
   $dbname      = "dbname=test1";
   $credentials = "user=postgres password=maxpoint!db";

   $conn = pg_connect( "$host $port $dbname $credentials"  );

   if (!$conn) {
      echo "error";
   } 

   $output = array();
   $result = pg_query($conn, "SELECT search_term FROM brandlist WHERE category = '$category'");

   while ($row = pg_fetch_assoc($result)) {
      array_push($output, $row['search_term']);
   }

   echo json_encode($output);
?>