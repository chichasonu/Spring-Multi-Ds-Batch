package com.spring.batch.example.sqlserver.repository;

import com.spring.batch.example.sqlserver.entities.SqlServerEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SqlServerRepository extends JpaRepository<SqlServerEntity,Integer> {
}
