package com.spring.batch.example.config;

import org.springframework.beans.factory.annotation.Configurable;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.orm.jpa.vendor.HibernateJpaVendorAdapter;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;

import javax.sql.DataSource;

@Configurable
@EnableTransactionManagement
@EnableJpaRepositories(basePackages = "com.spring.batch.example.mysql.repository",
                        entityManagerFactoryRef = "primaryEntityManager",
                        transactionManagerRef = "primaryTransactionManager")
public class PrimaryDataSourceConfiguration {

    @Value("${primary.datasource.mysql.driverClassName}")
    private String driverClassName;

    @Value("${primary.datasource.mysql.userName}")
    private String userName;

    @Value("${primary.datasource.mysql.password}")
    private String password;

    @Value("${primary.datasource.mysql.jdbcUrl}")
    private String jdbcUrl;

    @Bean(name = "primaryDataSource")
    public DataSource primaryDataSource(){
        DriverManagerDataSource driverManagerDataSource = new DriverManagerDataSource();
        driverManagerDataSource.setDriverClassName(driverClassName);
        driverManagerDataSource.setUrl(jdbcUrl);
        driverManagerDataSource.setUsername(userName);
        driverManagerDataSource.setPassword(password);
        return driverManagerDataSource;
    }

    @Bean(name = "primaryEntityManager")
    public LocalContainerEntityManagerFactoryBean entityManagerFactoryBean(){
        LocalContainerEntityManagerFactoryBean entityManagerFactoryBean = new LocalContainerEntityManagerFactoryBean();
        entityManagerFactoryBean.setDataSource(primaryDataSource());
        entityManagerFactoryBean.setPackagesToScan("com.spring.batch.example.mysql.entities");
        entityManagerFactoryBean.setPersistenceUnitName("PrimaryPersistenceUnit");
        HibernateJpaVendorAdapter jpaVendorAdapter = new HibernateJpaVendorAdapter();
        entityManagerFactoryBean.setJpaVendorAdapter(jpaVendorAdapter);
        return entityManagerFactoryBean;
    }

    @Bean(name = "primaryTransactionManager")
    public PlatformTransactionManager platformTransactionManager(){
        JpaTransactionManager jpaTransactionManager = new JpaTransactionManager();
        jpaTransactionManager.setEntityManagerFactory(entityManagerFactoryBean().getObject());
        return jpaTransactionManager;
    }
}
