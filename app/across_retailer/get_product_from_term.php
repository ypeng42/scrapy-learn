<?php
	class Product {
		var $product_name;
		var $img_url;
		var $retailer;
		var $url;

		function __construct($product, $img_url, $retailer, $url) {
			$this->product_name = $product;
			$this->img_url = $img_url;
			$this->retailer = $retailer;
			$this->url = $url;
		}
	}

	$search_term = $_POST["search_term"];

	$host        = "host=127.0.0.1";
	$port        = "port=5432";
	$dbname      = "dbname=test1";
	$credentials = "user=postgres password=maxpoint!db";

	$conn = pg_connect( "$host $port $dbname $credentials"  );

	if (!$conn) {
	  echo "error";
	} 

	$output = array();

	$sql = "SELECT product_name, image_url, retailer, url 
		FROM product_info 
		WHERE search_term = $1
		AND current_price IS NOT NULL";

	$result = pg_query_params($conn, $sql, array($search_term));

	while ($row = pg_fetch_assoc($result)) {
	  array_push($output, new Product($row['product_name'], $row['image_url'], $row['retailer'],
	  	$row['url']));
	}

	echo json_encode($output);

?>
