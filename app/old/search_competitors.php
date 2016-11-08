<?php
	$product_name = $_POST["product_name"];
	$retailer = $_POST["retailer"];
	$choice = $_POST["choice"];

	$exe_str = "/usr/lib/jvm/java-7-oracle/bin/java -jar /home/yuqing/Desktop/product-match/out/artifacts/search_jar/product-match.jar "."$choice \"$product_name\" \"$retailer\"";
	
	exec($exe_str, $output, $exit_code);

	echo $output[0];
?>