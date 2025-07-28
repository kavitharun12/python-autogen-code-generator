package com.example.pricecreation.error;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "product_price_error")
public class ProductPriceError {
    @Id
    private String id;
    private String ppid;
    private String season;
    private String errorMessage;

    // Getters and setters
}