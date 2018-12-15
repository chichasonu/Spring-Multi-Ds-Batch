package com.spring.batch.example.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.orm.jpa.vendor.HibernateJpaVendorAdapter;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;

import javax.sql.DataSource;

@Configuration
@EnableTransactionManagement
@EnableJpaRepositories(entityManagerFactoryRef = "secondaryEntityManager",
                       transactionManagerRef = "secondaryTransactionManager",
                       basePackages = "com.spring.batch.example.sqlserver.repository")
public class SecondaryDataSourceConfiguration {

    @Value("${primary.datasource.sqlServer.driverClassName}")
    private String driverClassName;

    @Value("${primary.datasource.sqlServer.userName}")
    private String userName;

    @Value("${primary.datasource.sqlServer.password}")
    private String password;

    @Value("${primary.datasource.sqlServer.jdbcUrl}")
    private String jdbcUrl;

    @Bean(name = "secondaryDataSource")
    public DataSource secondaryDataSource(){
        DriverManagerDataSource driverManagerDataSource = new DriverManagerDataSource();
        driverManagerDataSource.setDriverClassName(driverClassName);
        driverManagerDataSource.setUrl(jdbcUrl);
        driverManagerDataSource.setUsername(userName);
        driverManagerDataSource.setPassword(password);
        return driverManagerDataSource;
    }

    @Bean(name = "secondaryEntityManager")
    public LocalContainerEntityManagerFactoryBean entityManagerFactoryBean(){
        LocalContainerEntityManagerFactoryBean entityManagerFactoryBean = new LocalContainerEntityManagerFactoryBean();
        entityManagerFactoryBean.setDataSource(secondaryDataSource());
        entityManagerFactoryBean.setPackagesToScan("com.spring.batch.example.mysql.entities");
        HibernateJpaVendorAdapter jpaVendorAdapter = new HibernateJpaVendorAdapter();
        entityManagerFactoryBean.setJpaVendorAdapter(jpaVendorAdapter);
        return entityManagerFactoryBean;
    }

    @Bean(name = "secondaryTransactionManager")
    public PlatformTransactionManager platformTransactionManager(){
        JpaTransactionManager jpaTransactionManager = new JpaTransactionManager();
        jpaTransactionManager.setEntityManagerFactory(entityManagerFactoryBean().getObject());
        return jpaTransactionManager;
    }
}
