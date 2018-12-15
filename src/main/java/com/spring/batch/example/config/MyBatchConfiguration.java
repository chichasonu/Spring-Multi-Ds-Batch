package com.spring.batch.example.config;


import com.spring.batch.example.mysql.entities.MySqlEntity;
import com.spring.batch.example.sqlserver.entities.SqlServerEntity;
import com.sun.xml.internal.txw2.output.DataWriter;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;
import org.springframework.batch.core.configuration.annotation.JobBuilderFactory;
import org.springframework.batch.core.configuration.annotation.StepBuilderFactory;
import org.springframework.batch.core.launch.support.SimpleJobLauncher;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.batch.item.ItemWriter;
import org.springframework.batch.item.database.JpaItemWriter;
import org.springframework.batch.item.database.JpaPagingItemReader;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.orm.jpa.LocalEntityManagerFactoryBean;

@Configuration
@Import({PrimaryDataSourceConfiguration.class,SecondaryDataSourceConfiguration.class})
@EnableBatchProcessing
@ComponentScan(basePackageClasses = MyBatchConfigurer.class)
public class MyBatchConfiguration {

    @Autowired
    private StepBuilderFactory stepBuilderFactory;

    @Autowired
    private JobBuilderFactory jobBuilderFactory;

    @Autowired
    @Qualifier("secondaryEntityManager")
    private LocalContainerEntityManagerFactoryBean localContainerEntityManagerFactoryBean;

    @Autowired
    @Qualifier("primaryEntityManager")
    private LocalContainerEntityManagerFactoryBean getLocalContainerEntityManagerFactoryBean;

    @Bean
    public JpaPagingItemReader jpaPagingItemReader(){
        JpaPagingItemReader<SqlServerEntity> jpaPagingItemReader = new JpaPagingItemReader<>();
        jpaPagingItemReader.setPageSize(1000);
        jpaPagingItemReader.setMaxItemCount(1000);
        jpaPagingItemReader.setQueryString("select p from SqlServerEntity p");
        jpaPagingItemReader.setEntityManagerFactory(localContainerEntityManagerFactoryBean.getObject());
        return jpaPagingItemReader;
    }

    @Bean
    public JpaItemWriter jpaItemWriter(){
        JpaItemWriter<MySqlEntity> jpaItemWriter = new JpaItemWriter<>();
        jpaItemWriter.setEntityManagerFactory(getLocalContainerEntityManagerFactoryBean.getObject());
        return jpaItemWriter;
    }

    @Bean
    public ItemWriter itemWriter(){
        DatwWriter datwWriter = new DatwWriter();
        return datwWriter;
    }

    @Bean
    public SimpleJobLauncher simpleJobLauncher(JobRepository jobRepository){
        SimpleJobLauncher simpleJobLauncher = new SimpleJobLauncher();
        simpleJobLauncher.setJobRepository(jobRepository);
        return simpleJobLauncher;
    }

    @Bean
    public ItemProcessor itemProcessor(){
        return new DataItemProcessor();
    }

    @Bean
    public Step step(){
        return stepBuilderFactory.get("myStep").chunk(100).reader(jpaPagingItemReader())
               .processor(itemProcessor()).writer(jpaItemWriter()).build();
    }

    @Bean("myJob")
    public Job job(){
        return jobBuilderFactory.get("myJob").start(step()).build();
    }
}
