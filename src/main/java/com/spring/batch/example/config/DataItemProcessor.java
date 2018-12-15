package com.spring.batch.example.config;

import com.spring.batch.example.mysql.entities.MySqlEntity;
import com.spring.batch.example.sqlserver.entities.SqlServerEntity;
import org.springframework.batch.item.ItemProcessor;

public class DataItemProcessor implements ItemProcessor<SqlServerEntity, MySqlEntity> {


    @Override
    public MySqlEntity process(SqlServerEntity sqlServerEntity) throws Exception {
        MySqlEntity mySqlEntity = new MySqlEntity();
        mySqlEntity.setFirstName(sqlServerEntity.getFirstName());
        mySqlEntity.setId(sqlServerEntity.getId());
        return mySqlEntity;
    }
}
