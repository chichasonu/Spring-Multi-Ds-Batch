package com.spring.batch.example.mysql.repository;

import com.spring.batch.example.mysql.entities.MySqlEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MysqlEntityRepository extends JpaRepository<MySqlEntity,Integer> {

}
