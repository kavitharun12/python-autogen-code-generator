package com.example.pricecreation.stepdefinitions;

import com.example.pricecreation.models.Product;
import com.example.pricecreation.models.Price;
import io.cucumber.java.After;
import io.cucumber.java.Before;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.kafka.core.KafkaTemplate;

@CucumberOptions(features = "classpath:features/PriceCreation.feature")
public class StepDefinitions {
    @Autowired
    private MongoTemplate mongoTemplate;

    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;

    private Product product;
    private Price price;

    @Before
    public void setup() {
        // Initialize the product and price objects
    }

    // Implement step definitions for other scenarios in the feature file
}