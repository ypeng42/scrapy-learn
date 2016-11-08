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

	$search_term = $_POST["search_term"];
	$brand = $_POST['brand'];

	$host        = "host=127.0.0.1";
	$port        = "port=5432";
	$dbname      = "dbname=test1";
	$credentials = "user=postgres password=maxpoint!db";

	$conn = pg_connect( "$host $port $dbname $credentials"  );

	if (!$conn) {
	  echo "error";
	} 

	$retailer_arr = ["Target", "Sams Club", "Walmart", "CVS", "Dollar General", "Walgreens"];

	$output = array();

	foreach ($retailer_arr as $retailer) {
		$sql = "SELECT count(prod.product_name), sum(cast(price.current_price AS double precision)), price.date_crawled
				FROM product_info prod 
				LEFT JOIN product_price_info price 
				ON prod.product_name = price.product_name
				WHERE prod.search_term = $1
				AND prod.retailer = $2
				GROUP BY price.date_crawled";

		$result = pg_query_params($conn, $sql, array($search_term, $retailer));
		$daily_price = array();

		while ($row = pg_fetch_assoc($result)) {
			$daily_total = $row['sum'];
			$daily_count = $row['count'];
			array_push($daily_price, $daily_total / $daily_count);
		}

		if (!empty($daily_price)) {
			array_push($output, new RetailerPriceInfo($retailer, average($daily_price), variance($daily_price)));
		}
	}

	echo json_encode($output);
?>