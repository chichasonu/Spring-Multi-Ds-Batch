package com.spring.batch.example.config;

import com.spring.batch.example.mysql.entities.MySqlEntity;
import org.springframework.batch.item.ItemWriter;

import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import java.util.List;

public class DatwWriter implements ItemWriter<MySqlEntity> {

    @PersistenceContext(name = "PrimaryPersistenceUnit")
    EntityManager entityManager;

    @Override
    public void write(List<? extends MySqlEntity> list) throws Exception {
        for (MySqlEntity mySqlEntity:
             list) {
            entityManager.persist(mySqlEntity);
        }
    }
}
