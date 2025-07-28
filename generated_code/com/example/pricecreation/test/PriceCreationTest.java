package com.example.pricecreation.test;

import io.cucumber.junit.Cucumber;
import io.cucumber.junit.CucumberOptions;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@CucumberOptions(
        features = "classpath:src/test/resources/features",
        glue = "com.example.pricecreation.steps"
)
public class PriceCreationTest {

    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;

    // Add tests for other components, such as Product, Price, PriceRepository, and PriceService, as needed.
}