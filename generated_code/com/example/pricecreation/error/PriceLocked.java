package com.example.pricecreation.error;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "price_locked")
public class PriceLocked {
    @Id
    private String id;
    private String ppid;
    private String season;
    private boolean isLocked;

    // Getters and setters
}