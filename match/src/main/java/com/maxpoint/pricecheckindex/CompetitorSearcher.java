package com.maxpoint.pricecheckindex;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.*;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import java.io.IOException;
import java.nio.file.Paths;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class CompetitorSearcher {
    private Directory indexDir;
    private IndexWriter w;
    private Connection conn;

    public CompetitorSearcher() throws Exception {
        indexDir = FSDirectory.open(Paths.get(Settings.INDEX_DIRECTORY));
        Class.forName(Settings.JDBC_DRIVER);
        conn = DriverManager.getConnection(Settings.DB_URL, Settings.USER, Settings.PASS);
    }

    public static void main(String[] args) throws Exception {
        String choice = args[0];
        String product = args[1];
        String retailer = args[2];

        CompetitorSearcher demo = new CompetitorSearcher();
        demo.run(choice, product, retailer);
    }

    private void run(String choice, String product, String retailer) {
        if (choice.equals("retailer")) {

            ProductItem currItem = new ProductItem.Builder(product, retailer).build();
            search(currItem, getRetailerList(currItem), choice);

        } else if (choice.equals("brand")) {
            ProductItem currItem = new ProductItem.Builder(product, retailer).build();
            search(currItem, getBrandList(currItem), choice);
        }
    }

    private void search(ProductItem item, List<String> searchList, String key) {
        try {
            int hitsPerPage = 20;

            IndexReader reader = DirectoryReader.open(indexDir);
            IndexSearcher searcher = new IndexSearcher(reader);

            List<ProductItem> potentialMatch = new ArrayList<ProductItem>();

            for (String searchItem : searchList) {
                BooleanQuery.Builder combine = new BooleanQuery.Builder();

                Query q1 = new QueryParser("product", new StandardAnalyzer()).parse
                        ("product:" + QueryParser.escape(item.getProduct()));
                combine.add(q1, BooleanClause.Occur.SHOULD);

                Query q2 = new QueryParser(key, new StandardAnalyzer()).parse
                        (key + ":" + QueryParser.escape(searchItem));
                combine.add(q2, BooleanClause.Occur.MUST);

                ScoreDoc[] hits = searcher.search(combine.build(), hitsPerPage).scoreDocs;

                if (hits.length <= 0) {
                    System.out.println("No match found for " + searchItem);
                    continue;
                }

                double cutoff = 0;
                ProductItem originProduct = item;
                ProductItem bestMatch = null;

                for (int i = 0; i < hits.length; i++) {
                    int docId = hits[i].doc;
                    Document d = searcher.doc(docId);

                    if (ProductMatchUtil.getJaccardIndex(d.get("product"), originProduct.getProduct()) < cutoff)
                        continue;

                    ProductItem currProduct = new ProductItem.Builder(d.get("product"), d.get("retailer")).build();
                    currProduct.setBrand(d.get("brand"));
                    currProduct.setSimilarity(ProductMatchUtil.getJaccardIndex(currProduct.getProduct(), originProduct.getProduct()));
                    currProduct.setPrice(Double.parseDouble(d.get("price")));
                    currProduct.setImageURL(d.get("imageUrl"));
                    currProduct.setURL(d.get("url"));

                    bestMatch = currProduct;
                    cutoff = ProductMatchUtil.getJaccardIndex(currProduct.getProduct(), originProduct.getProduct());
                }

                if (bestMatch == null)
                    continue;

                potentialMatch.add(bestMatch);
            }

            JSONArray jsonArray = new JSONArray();
            for (ProductItem p : potentialMatch) {
                JSONObject obj = new JSONObject();
                obj.put("product_name", p.getProduct());
                obj.put("retailer", p.getRetailer());
                obj.put("img_url", p.getImageURL());
                obj.put("url", p.getURL());
                obj.put("brand", p.getBrand());
                obj.put("price", p.getPrice());
                obj.put("score", p.getSimilarity());
                jsonArray.add(obj);
//                System.out.format("%-3s %-80s %-30s %-30s %-4s\n",
//                        Integer.toString(i),
//                        p.getProduct(),
//                        p.getRetailer(),
//                        p.getBrand(),
//                        p.getSimilarity()
//                );
//                i++;
            }

            System.out.print(jsonArray.toJSONString());
        } catch (IOException e) {
            e.printStackTrace();
        } catch (ParseException e) {
            e.printStackTrace();
        }
    }

    private List<String> getRetailerList(ProductItem item) {
        String[] list = {"CVS", "Target", "Walmart", "Walgreens", "Dollar General", "Sams Club"};
        List<String> output = new ArrayList<String>();
        for (String s : list) {
            if (!s.equals(item.getRetailer())) {
                output.add(s);
            }
        }

        return output;
    }

    private List<String> getBrandList(ProductItem item) {
        List<String> output = new ArrayList<String>();
        try {
            PreparedStatement query = conn.prepareStatement("SELECT brand FROM product_info WHERE product_name = ? AND retailer = ?");
            query.setString(1, item.getProduct());
            query.setString(2, item.getRetailer());
            ResultSet rs = query.executeQuery();
            String brand = "";

            if (rs.next()) {
                brand = rs.getString("brand");
                item.setBrand(brand);
            }

            query = conn.prepareStatement("SELECT category FROM brandlist WHERE brand = ?");
            query.setString(1, brand);
            rs = query.executeQuery();
            String category = "";

            if (rs.next()) {
                category = rs.getString("category");
            }

            query = conn.prepareStatement("SELECT brand FROM brandlist WHERE category = ?");
            query.setString(1, category);
            rs = query.executeQuery();

            while (rs.next()) {
                if (rs.getString("brand").equals(item.getBrand()))
                    continue;

                output.add(rs.getString("brand"));
            }

        } catch(SQLException e) {
            e.printStackTrace();
        }

        return output;
    }
}
