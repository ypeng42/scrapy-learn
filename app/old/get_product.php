<?php
	class Product {
		var $product_name;
		var $retailer;
		var $img_url;
		var $url;
		var $brand;
		var $price;

		function __construct($product, $retailer, $img_url, $url, $brand, $price) {
			$this->product_name = $product;
			$this->retailer = $retailer;
			$this->img_url = $img_url;
			$this->url = $url;
			$this->brand = $brand;
			$this->price = $price;
		}
	}

	$brand = $_POST["brand"];

	$host        = "host=127.0.0.1";
	$port        = "port=5432";
	$dbname      = "dbname=test1";
	$credentials = "user=postgres password=123";

	$conn = pg_connect( "$host $port $dbname $credentials"  );

	if (!$conn) {
	  echo "error";
	} 

	if ($brand == "Huggies") {
		$result = pg_query($conn, "SELECT * FROM product_info WHERE brand LIKE '$brand%'");
	} else {
		$result = pg_query($conn, "SELECT * FROM product_info WHERE brand = '$brand'");
	}

	$product_arr = array();

	while ($row = pg_fetch_assoc($result)) {
		array_push($product_arr, new Product($row['product_name'], $row['retailer'], $row['image_url'], $row['url'], $row['brand'], $row['current_price']));
	}

	echo json_encode($product_arr);
?>