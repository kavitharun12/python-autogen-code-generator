package com.example.pricecreation.controllers;

import com.example.pricecreation.models.Product;
import com.example.pricecreation.models.Price;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class KafkaController {
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;

    @Autowired
    private PriceService priceService;

    @PostMapping("/postPrice")
    public void postPrice(@RequestBody Product product, @RequestParam("season") String season) {
        priceService.createPrice(product, season);
        String message = "Price created for ppid " + product.getPpid() + ", season " + season;
        kafkaTemplate.send("price-topic", message);
    }
}