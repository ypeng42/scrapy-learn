<?php
	function average($arr) {
		if (!is_array($arr)) return 0;
		return array_sum($arr) / count($arr);
	}

	function variance($aValues, $bSample = false) {
		$fMean = array_sum($aValues) / count($aValues);
		$fVariance = 0.0;

		foreach ($aValues as $i) {
			$fVariance += pow($i - $fMean, 2);
		}

		$fVariance /= ( $bSample ? count($aValues) - 1 : count($aValues) );
		return $fVariance;
	}

	class ProductInfo {
		var $product_name;
		var $retailer;
		var $count_no;
		var $volume_no;
		var $pack_no;
		var $average_price;
		var $variance;
		var $url;

		function __construct($product_name, $retailer, $count_no, $volume_no, $pack_no, $url) {
			$this->product_name = $product_name;
			$this->retailer = $retailer;
			$this->count_no = $count_no;
			$this->volume_no = $volume_no;
			$this->pack_no = $pack_no;
			$this->url = $url;
		}

		function setAverage($average_price) {
			$this->average_price = $average_price;
		}

		function setVariance($variance) {
			$this->variance = $variance;
		}
	} 

	class RetailerPriceInfo {
		var $retailer;
		var $average;
		var $variance;

		function __construct($retailer, $average, $variance) {
			$this->retailer = $retailer;
			$this->average = $average;
			$this->variance = $variance;
		}
	}


	$plist = $_POST['plist'];
	// $retailer_list = $_POST['retailer_list'];
	$retailer_list = array();

	$host        = "host=127.0.0.1";
	$port        = "port=5432";
	$dbname      = "dbname=test1";
	$credentials = "user=postgres password=maxpoint!db";

	$conn = pg_connect( "$host $port $dbname $credentials"  );

	if (!$conn) {
	  echo "error";
	} 


	$product_info = array();
	$new_plist = array();

	// #############################################
	// Get information of each product selected
	// #############################################
	foreach ($plist as $p_str) {
		$product = split('#', $p_str)[0];
		$retailer = split('#', $p_str)[1];

		// Make a product list
		array_push($new_plist, $product);
		if (!in_array($retailer, $retailer_list)) {
			array_push($retailer_list, $retailer);
		}

		// #############################################
		// Get basic product information
		// #############################################
		$sql = "SELECT product_name, retailer, count_no, volume_no, pack_no, url
			FROM product_info 
			WHERE product_name = $1
			AND retailer = $2";

		$result = pg_query_params($conn, $sql, array($product, $retailer));
		
		$row = pg_fetch_assoc($result);

		$p_info = new ProductInfo($row['product_name'], $row['retailer'], $row['count_no'], $row['volume_no'], $row['pack_no'], $row['url']);


		// #############################################
		// Get average price of the product
		// #############################################
		$sql = "SELECT count(product_name), sum(cast(current_price AS double precision)) 
				FROM product_price_info 
				WHERE product_name = $1
				AND retailer = $2
				GROUP BY date_crawled;";

		$result = pg_query_params($conn, $sql, array($product, $retailer));
		
		$product_daily_price = array();

		while ($row = pg_fetch_assoc($result)) {
			if ($row['sum'] != NULL) {
				array_push($product_daily_price, $row['sum'] / $row['count']);
			}
		}

		if (!empty($product_daily_price)) {
			$p_info->setAverage(average($product_daily_price));

			$p_info->setVariance(variance($product_daily_price));
		}

		array_push($product_info, $p_info);

	}


	// #############################################
	// Get pricing information at each retailer
	// #############################################
	$price_info = array();

	foreach ($retailer_list as $retailer) {

		$sql = "SELECT count(product_name), sum(cast(current_price AS double precision)) 
			FROM product_price_info 
			WHERE product_name = ANY($1)
			AND retailer = $2
			GROUP BY date_crawled;";

		$result = pg_query_params($conn, $sql, array("{".implode(',', $new_plist)."}", $retailer));
		
		// Average price of all product from that retailer in a day
		$daily_price = array();

		while ($row = pg_fetch_assoc($result)) {
			if ($row['sum'] != NULL) {
				array_push($daily_price, $row['sum'] / $row['count']);
			}
		}

		if (!empty($daily_price)) {
			array_push($price_info, new RetailerPriceInfo($retailer, average($daily_price), variance($daily_price)));
		}
	}


	echo json_encode((object) ['price_info' => $price_info, 'product_info' => $product_info])

?>