package com.spring.batch.example;

import org.springframework.batch.core.launch.support.CommandLineJobRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ExampleMainApplication {

    public static void main(String[] args) throws Exception{
        SpringApplication.run(ExampleMainApplication.class,args);
        CommandLineJobRunner.main(new String[]{"com.spring.batch.example.config.MyBatchConfiguration","myJob"});
    }
}
