package com.spring.batch.example.config;

import org.springframework.batch.core.configuration.annotation.DefaultBatchConfigurer;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.repository.support.MapJobRepositoryFactoryBean;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;
import org.springframework.transaction.PlatformTransactionManager;

import javax.sql.DataSource;

@Component
public class MyBatchConfigurer extends DefaultBatchConfigurer {

    @Autowired
    @Qualifier(value = "primaryDataSource")
    DataSource myPrimaryDataSource;

    @Autowired
    @Qualifier(value = "primaryTransactionManager")
    PlatformTransactionManager platformTransactionManager;

    @Override
    public void setDataSource(DataSource dataSource) {
        super.setDataSource(myPrimaryDataSource);
    }

    @Override
    public PlatformTransactionManager getTransactionManager() {
        return platformTransactionManager;
    }

    @Override
    protected JobRepository createJobRepository() throws Exception {
        return customJobRepository();
    }

    public JobRepository customJobRepository() throws Exception {
        MapJobRepositoryFactoryBean mapJobRepositoryFactoryBean = new MapJobRepositoryFactoryBean(platformTransactionManager);
        return mapJobRepositoryFactoryBean.getObject();
    }
}
