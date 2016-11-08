<?php
	class Product {
		var $product_name;
		var $img_url;
		var $search_term;
		var $url;

		function __construct($product, $img_url, $search_term, $url) {
			$this->product_name = $product;
			$this->img_url = $img_url;
			$this->search_term = $search_term;
			$this->url = $url;
		}
	}

	$search_terms = $_POST["search_terms"];
	$retailer = $_POST["retailer"];

	$host        = "host=127.0.0.1";
	$port        = "port=5432";
	$dbname      = "dbname=test1";
	$credentials = "user=postgres password=maxpoint!db";

	$conn = pg_connect( "$host $port $dbname $credentials" );

	if (!$conn) {
	  echo "error";
	} 

	$output = array();

	foreach ($search_terms as $search_term) {
		$sql = "SELECT product_name, image_url, search_term , url
				FROM product_info 
				WHERE search_term = $1
				AND retailer = $2
				AND current_price IS NOT NULL";

		$result = pg_query_params($conn, $sql, array($search_term, $retailer));

		while ($row = pg_fetch_assoc($result)) {
		  	array_push($output, new Product($row['product_name'], $row['image_url'], $row['search_term'], $row['url']));
		}
	}
	
	

	echo json_encode($output);

?>
