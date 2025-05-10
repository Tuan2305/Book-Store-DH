CREATE DATABASE IF NOT EXISTS `defaultdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `defaultdb`;
-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)

DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `email` varchar(100) NOT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `username` varchar(50) DEFAULT NULL,
  `phone_number` varchar(50) DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `date_joined` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '0',
  `is_admin` tinyint(1) DEFAULT '0',
  `is_staff` tinyint(1) DEFAULT '0',
  `is_superadmin` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts`
--

LOCK TABLES `accounts` WRITE;
/*!40000 ALTER TABLE `accounts` DISABLE KEYS */;
INSERT INTO `accounts` VALUES (1,'pbkdf2_sha256$600000$ahGkLvPA7uXfRw5gM9pkAk$uGHkfRcrVrrq/R+m6OiFUU4lcWab6AEv5vMmkCpC1rE=','tuanpham@gmail.com','tuan','dep trai','tuanpham@gmail.com','0123456789','2023-06-08 02:33:00','2023-06-08 02:30:00',1,1,1,1),(2,'pbkdf2_sha256$600000$8kNGBkMMXJdpu2U9M2QOKg$fsKSrlwl75hjV8+MU0zyJV0sZTW6BHRDuVBA3rcGF8I=','jjjaeseok@gmail.com','Taylor','Swift','jjjaeseok','0987654321','2023-06-05 12:45:00','2023-06-05 12:42:00',1,0,0,0),(3,'pbkdf2_sha256$600000$I8SlfPwKrTR9qJAoS9JCMv$TwIyUwTFVFPvr2O0PYGY2EUKu6nb2987yucagRz0YHk=','vju@gmail.com','Linh','Bui','bkl','0123456789','2024-06-02 11:51:00','2023-06-05 12:38:00',1,0,0,0);
/*!40000 ALTER TABLE `accounts` ENABLE KEYS */;
UNLOCK TABLES;