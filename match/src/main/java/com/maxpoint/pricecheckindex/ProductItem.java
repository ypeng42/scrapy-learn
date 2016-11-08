package com.maxpoint.pricecheckindex;

public class ProductItem {
    private String product;
    private String retailer;
    private Double price;
    private String brand;
    private String breadcrumb;
    private String url;
    private String imageUrl;
    private double similarity;

    private ProductItem(Builder builder) {
        this.product = builder.product;
        this.retailer = builder.retailer;
        this.price = builder.price;
        this.brand = builder.brand;
        this.breadcrumb = builder.breadcrumb;
        this.url = builder.url;
        this.imageUrl = builder.imageUrl;
        this.similarity = builder.similarity;
    }

    public static class Builder {
        // Required
        private String product;
        private String retailer;

        // Optional
        private Double price = -1.0;
        private String brand = "";
        private String breadcrumb = "";
        private String url = "";
        private String imageUrl = "";
        private double similarity = 0.0;

        public Builder(String product, String retailer) {
            this.product = product;
            this.retailer = retailer;
        }

        public Builder price(double price) {
            this.price = price;
            return this;
        }

        public Builder brand(String brand) {
            this.brand = brand;
            return this;
        }

        public Builder breadcrumb(String breadcrumb) {
            this.breadcrumb = breadcrumb;
            return this;
        }

        public Builder url(String url) {
            this.url = url;
            return this;
        }

        public Builder imageUrl(String imageUrl) {
            this.imageUrl = imageUrl;
            return this;
        }

        public Builder similarity(double similarity) {
            this.similarity = similarity;
            return this;
        }

        public ProductItem build() {return new ProductItem(this); }

    }

    public boolean isSameProduct (ProductItem product) {
        return getProduct().equals(product.getProduct()) && getRetailer().equals(product.getRetailer());
    }

    public boolean isSameRetailer (ProductItem product) {
        return product.getRetailer().equals(getRetailer());
    }

    public boolean isSameBrand (ProductItem product) {
        String b1 = product.getBrand().toLowerCase();
        String b2 = getBrand().toLowerCase();
        if (b1.contains("N/A") || b2.contains("N/A"))
            return false;
        if (b1.contains(b2) || b2.contains(b1))
            return true;

        return false;
    }

    public void setSimilarity(double similarity) { this.similarity = similarity; }

    public void setURL(String url) {
        this.url = url;
    }

    public void setPrice(double price) {
        this.price = price;
    }

    public void setBrand(String brand) {
        this.brand = brand;
    }

    public void setImageURL(String url) {
        this.imageUrl = url;
    }

    public String getProduct() {
        return product;
    }

    public Double getPrice() { return price; }

    public  String getPriceString() {
        return price == -1 ? "N/A" : price.toString();
    }

    public String getBrand() {
        return brand;
    }

    public double getSimilarity() { return similarity; }

    public String getRetailer() {
        return retailer;
    }

    public String getURL() { return url; }

    public String getImageURL() { return imageUrl; }

    public String getBreadcrumb() { return breadcrumb; }

    public String toString() {
        return getProduct() + " ( " + getPriceString() + " ) " + getSimilarity()
                + " " + getURL();
    }
}