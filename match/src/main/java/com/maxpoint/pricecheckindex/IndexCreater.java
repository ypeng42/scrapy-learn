package com.maxpoint.pricecheckindex;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.*;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

import java.io.IOException;
import java.nio.file.Paths;
import java.sql.*;
import java.util.Scanner;

public class IndexCreater {

    private Directory indexDir;
    private IndexWriter w;
    private Connection conn;
    private Scanner input;

    public IndexCreater() throws Exception {
        indexDir = FSDirectory.open(Paths.get(Settings.INDEX_DIRECTORY));
        Class.forName(Settings.JDBC_DRIVER);
        conn = DriverManager.getConnection(Settings.DB_URL, Settings.USER, Settings.PASS);
        input = new Scanner(System.in);
    }

    public static void main(String[] args) throws Exception {
        IndexCreater demo = new IndexCreater();
        demo.run();
    }

    private void run() throws Exception {
        // Index all the products crawled
        createIndex();

        // Some product don't have brand, need to infer it in this step
        brandInference();
    }

    private void brandInference() {
        try {
            StandardAnalyzer analyzer = new StandardAnalyzer();
            IndexWriterConfig config = new IndexWriterConfig(analyzer);
            config.setOpenMode(IndexWriterConfig.OpenMode.APPEND);
            w = new IndexWriter(indexDir, config);

            PreparedStatement query = conn.prepareStatement("SELECT * FROM product_info WHERE brand is null");

            System.out.println("Reading product without brand");

            ResultSet rs = query.executeQuery();

            while (rs.next()) {
                IndexReader reader = DirectoryReader.open(indexDir);
                IndexSearcher searcher = new IndexSearcher(reader);

                String productName = rs.getString("product_name");
                Query q1 = new QueryParser("product", new StandardAnalyzer()).parse("product:" + QueryParser.escape(productName));;

                int hitsPerPage = 30;
                ScoreDoc[] hits = searcher.search(q1, hitsPerPage).scoreDocs;

                double cutoff = 0.2;
                ProductItem originProduct = new ProductItem.Builder(productName, rs.getString("retailer")).build();
                ProductItem bestMatch = null;

                for (int i = 0; i < hits.length; i++) {
                    int docId = hits[i].doc;
                    Document d = searcher.doc(docId);
                    String currBrand = d.get("brand");
                    String currName = d.get("product");

                    ProductItem currProduct = new ProductItem.Builder(d.get("product"), d.get("retailer")).brand(currBrand).build();

                    if (currProduct.isSameProduct(originProduct)) {
                        continue;
                    }

                    if (currBrand.equals("N/A"))
                        continue;

                    if (ProductMatchUtil.getJaccardIndex(currProduct.getProduct(), originProduct.getProduct()) < cutoff)
                        continue;

                    if (currProduct.getProduct().toLowerCase().contains(currBrand.toLowerCase()) &&
                            !originProduct.getProduct().toLowerCase().contains(currBrand.toLowerCase()))
                        continue;

                    bestMatch = currProduct;
                    cutoff = ProductMatchUtil.getJaccardIndex(currProduct.getProduct(), originProduct.getProduct());
                }

                if (bestMatch == null)
                    continue;

//                int no = rs.getInt("no");
//                Query deleteQuery = NumericRangeQuery.newIntRange("no", no, no, true, true);
//                w.deleteDocuments(deleteQuery);

                writeToIndex(rs, bestMatch.getBrand());

                // Update brand in database
                query = conn.prepareStatement("UPDATE product_info SET brand = ? WHERE product_name = ? AND retailer = ?");
                query.setString(1, bestMatch.getBrand());
                query.setString(2, originProduct.getProduct());
                query.setString(3, originProduct.getRetailer());

                query.executeUpdate();
            }

            w.close();
            System.out.println("Finished Brand Inference");

        } catch (SQLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (ParseException e) {
            e.printStackTrace();
        }
    }

    private void createIndex() {
        StandardAnalyzer analyzer = new StandardAnalyzer();
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND);

        try {
            w = new IndexWriter(indexDir, config);

            PreparedStatement query = conn.prepareStatement("SELECT * FROM product_info WHERE new_item = ?");
            query.setBoolean(1, true);
            ResultSet rs = query.executeQuery();

            while (rs.next()) {

                // Product without brand will be indexed in brand inference step
                if (rs.getString("brand") != null) {
                    writeToIndex(rs, null);
                }

                PreparedStatement updateQuery = conn.prepareStatement
                        ("UPDATE product_info SET new_item = ? WHERE product_name = ? AND retailer = ?");
                updateQuery.setBoolean(1, false);
                updateQuery.setString(2, rs.getString("product_name"));
                updateQuery.setString(3, rs.getString("retailer"));
                updateQuery.executeUpdate();
            }

            w.close();

        } catch (SQLException se) {

            se.printStackTrace();

        } catch (IOException e) {

            e.printStackTrace();

        } catch (Exception e) {

            e.printStackTrace();

        } finally {

            System.out.println("Done Updating Index");

        }
    }

    private void writeToIndex (ResultSet rs, String b) {
        Document doc = new Document();
        try {
            int no = rs.getInt("no");
            String product = rs.getString("product_name") == null ? "N/A" : rs.getString("product_name");
            String price = rs.getString("current_price") == null ? "N/A" : rs.getString("current_price");
            String retailer = rs.getString("retailer") == null ? "N/A" : rs.getString("retailer");
            String url = rs.getString("url") == null ? "N/A" : rs.getString("url");
            String imageUrl = rs.getString("image_url") == null ? "N/A" : rs.getString("image_url");

            String brand = b == null ? rs.getString("brand") : b;

            doc.add(new IntField("no", no, Field.Store.YES));
            doc.add(new TextField("product", product, Field.Store.YES));
            doc.add(new DoubleField("price", parsePrice(price), Field.Store.YES));
            doc.add(new TextField("brand", brand, Field.Store.YES));
            doc.add(new TextField("retailer", retailer, Field.Store.YES));
            doc.add(new TextField("url", url, Field.Store.YES));
            doc.add(new TextField("imageUrl", imageUrl, Field.Store.YES));

            w.addDocument(doc);
        } catch (SQLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private Double parsePrice(String priceStr) {
        if (priceStr == null)
            return -1.0;

        double number;

        if (priceStr.contains("-")) {
            number = Double.parseDouble(priceStr.split("-")[0]);
        } else if (priceStr.contains(" ")) {
            number = -1.0;
        } else {
            number = Double.parseDouble(priceStr);
        }

        return number;
    }
}
