package com.example.pricecreation.steps.stepdefinitions;

import com.example.pricecreation.models.Product;
import com.example.pricecreation.models.Price;
import com.example.pricecreation.repositories.PriceRepository;
import com.example.pricecreation.services.PriceService;
import io.cucumber.java.After;
import io.cucumber.java.Before;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.junit.jupiter.api.Assertions;
import org.mockito.Mock;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.List;
import java.util.Optional;

import static org.mockito.Mockito.*;

public class StepDefinitions {
    @Mock
    private PriceRepository priceRepository;

    @Mock
    private PriceService priceService;

    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;

    // Store instances of Product and Price for later use
    private Product product;
    private Price price;

    @Before
    public void setup() {
        // Initialize the product and price objects
    }

    // Implement step definitions for other scenarios in the feature file
}