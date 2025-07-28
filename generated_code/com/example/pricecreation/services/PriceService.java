package com.example.pricecreation.services;

import com.example.pricecreation.models.Product;
import com.example.pricecreation.models.Price;
import com.example.pricecreation.repositories.PriceRepository;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class PriceService {
    @Autowired
    private PriceRepository priceRepository;

    public void createPrice(Product product, String season) {
        Price price = new Price();
        price.setPpid(product.getPpid());
        price.setSeason(season);
        price.setPrice(/* calculate price here */);

        priceRepository.save(price);
    }
}