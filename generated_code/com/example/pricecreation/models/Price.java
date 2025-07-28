package com.example.pricecreation.models;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "prices")
public class Price {
    @Id
    private String id;
    private String ppid;
    private String season;
    private double price;

    // Getters and setters
}