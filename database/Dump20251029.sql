-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: ong_management
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `adhesiones_eventos_externos`
--

DROP TABLE IF EXISTS `adhesiones_eventos_externos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `adhesiones_eventos_externos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `evento_externo_id` int DEFAULT NULL,
  `voluntario_id` int DEFAULT NULL,
  `fecha_adhesion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `estado` enum('PENDIENTE','CONFIRMADA','CANCELADA','RECHAZADA') COLLATE utf8mb4_unicode_ci DEFAULT 'PENDIENTE',
  `datos_voluntario` json DEFAULT NULL,
  `fecha_aprobacion` timestamp NULL DEFAULT NULL,
  `motivo_rechazo` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `evento_externo_id` (`evento_externo_id`,`voluntario_id`),
  KEY `idx_adhesiones_evento_externo` (`evento_externo_id`),
  KEY `idx_adhesiones_voluntario` (`voluntario_id`),
  KEY `idx_adhesiones_estado` (`estado`),
  KEY `idx_adhesiones_estado_fecha` (`estado`,`fecha_adhesion` DESC),
  KEY `idx_adhesiones_aprobacion` (`fecha_aprobacion`)
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Tabla de adhesiones a eventos externos con sistema de aprobación';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `adhesiones_eventos_externos`
--

LOCK TABLES `adhesiones_eventos_externos` WRITE;
/*!40000 ALTER TABLE `adhesiones_eventos_externos` DISABLE KEYS */;
INSERT INTO `adhesiones_eventos_externos` VALUES (1,1,4,'2025-09-30 21:42:44','CONFIRMADA',NULL,NULL,NULL),(2,1,5,'2025-09-30 21:42:44','PENDIENTE',NULL,NULL,NULL),(3,2,3,'2025-09-30 21:42:44','CONFIRMADA',NULL,NULL,NULL),(4,3,4,'2025-09-30 21:42:44','PENDIENTE',NULL,NULL,NULL),(5,101,1,'2025-09-30 22:26:37','CONFIRMADA','{\"skills\": \"Organización\", \"availability\": \"Mañana\"}',NULL,NULL),(6,101,2,'2025-09-30 22:26:37','PENDIENTE','{\"skills\": \"Primeros auxilios\", \"availability\": \"Todo el día\"}',NULL,NULL),(7,102,1,'2025-09-30 22:26:37','CONFIRMADA','{\"skills\": \"Educación ambiental\", \"availability\": \"Tarde\"}',NULL,NULL),(8,103,3,'2025-09-30 22:26:37','PENDIENTE','{\"skills\": \"Atención al público\", \"availability\": \"Mañana\"}',NULL,NULL),(9,101,11,'2025-09-30 23:35:40','CONFIRMADA','{\"name\": \"Juan\", \"email\": \"admin@empujecomunitario.org\", \"phone\": \"\", \"surname\": \"Pérez\"}',NULL,NULL),(19,101,14,'2025-09-30 23:36:14','CONFIRMADA','{\"name\": \"AnaSAT\", \"email\": \"ana@empujecomunitario.org\", \"phone\": \"\", \"surname\": \"Martínez\"}',NULL,NULL),(21,21,17,'2025-10-06 01:21:14','CONFIRMADA','{\"name\": \"María\", \"email\": \"maria@esperanza.org\", \"phone\": \"\", \"surname\": \"González\"}',NULL,NULL),(22,20,17,'2025-10-06 01:48:12','CANCELADA','{\"name\": \"María\", \"email\": \"maria@esperanza.org\", \"phone\": \"\", \"surname\": \"González\"}',NULL,NULL),(25,24,17,'2025-10-11 21:38:17','CONFIRMADA','{\"name\": \"María\", \"email\": \"maria@esperanza.org\", \"phone\": \"\", \"surname\": \"González\"}','2025-10-12 01:02:45',NULL),(26,25,11,'2025-10-11 23:45:27','PENDIENTE','{\"name\": \"Juan\", \"email\": \"admin@empujecomunitario.org\", \"phone\": \"\", \"surname\": \"Pérez\", \"volunteer_id\": 11}',NULL,NULL),(29,26,11,'2025-10-11 23:58:48','RECHAZADA','{\"name\": \"Juan\", \"email\": \"admin@empujecomunitario.org\", \"phone\": \"\", \"surname\": \"Pérez\", \"volunteer_id\": 11}','2025-10-12 15:08:39','Sin motivo especificado'),(30,27,11,'2025-10-12 19:29:04','PENDIENTE','{\"name\": \"Juan\", \"email\": \"admin@empujecomunitario.org\", \"phone\": \"\", \"surname\": \"Pérez\", \"volunteer_id\": 11}',NULL,NULL),(33,28,11,'2025-10-12 19:40:15','CONFIRMADA','{\"name\": \"Juan\", \"email\": \"admin@empujecomunitario.org\", \"phone\": \"\", \"surname\": \"Pérez\", \"volunteer_id\": 11}','2025-10-12 19:40:28',NULL),(35,27,26,'2025-10-12 19:44:54','CONFIRMADA','{\"email\": \"test.notification@example.com\", \"nombre\": \"Test Notification 1760298294\", \"telefono\": \"555666777\", \"experiencia\": \"Test completo de notificaciones\"}','2025-10-12 19:44:55',NULL),(36,31,17,'2025-10-12 22:09:31','CONFIRMADA','{\"email\": \"voluntario@test.com\", \"nombre\": \"Voluntario Test\", \"telefono\": \"123456789\"}',NULL,NULL),(37,32,17,'2025-10-12 22:11:41','CANCELADA','{\"email\": \"maria@esperanza.org\", \"nombre\": \"María González\", \"skills\": \"Organización de eventos\", \"telefono\": \"123456789\", \"availability\": \"Fines de semana\"}','2025-10-12 22:11:41',NULL),(38,29,11,'2025-10-12 22:20:32','CONFIRMADA','{\"name\": \"Juan\", \"email\": \"admin@empujecomunitario.org\", \"phone\": \"\", \"surname\": \"Pérez\"}','2025-10-12 22:20:42',NULL),(39,33,11,'2025-10-12 22:22:08','CANCELADA','{\"name\": \"Juan\", \"email\": \"admin@empujecomunitario.org\", \"phone\": \"\", \"surname\": \"Pérez\"}',NULL,NULL),(40,34,17,'2025-10-12 22:22:34','CONFIRMADA','{\"email\": \"debug@test.com\", \"nombre\": \"Voluntario Debug\", \"telefono\": \"123456789\"}',NULL,NULL),(41,35,17,'2025-10-12 22:23:36','CANCELADA','{\"email\": \"debug@test.com\", \"nombre\": \"Voluntario Debug\", \"telefono\": \"123456789\"}',NULL,NULL),(42,36,17,'2025-10-12 22:24:21','CANCELADA','{\"email\": \"debug@test.com\", \"nombre\": \"Voluntario Debug\", \"telefono\": \"123456789\"}',NULL,NULL),(43,37,17,'2025-10-12 22:25:04','CANCELADA','{\"email\": \"debug@test.com\", \"nombre\": \"Voluntario Debug\", \"telefono\": \"123456789\"}',NULL,NULL),(44,38,17,'2025-10-12 22:26:10','CANCELADA','{\"email\": \"maria@esperanza.org\", \"nombre\": \"María González\", \"telefono\": \"123456789\"}',NULL,NULL),(45,39,17,'2025-10-12 22:27:33','CANCELADA','{\"email\": \"maria@esperanza.org\", \"nombre\": \"María González\", \"telefono\": \"123456789\"}',NULL,NULL),(46,40,17,'2025-10-12 22:30:43','CANCELADA','{\"email\": \"maria@esperanza.org\", \"nombre\": \"María González\", \"telefono\": \"123456789\"}',NULL,NULL),(47,41,17,'2025-10-12 22:33:33','CANCELADA','{\"email\": \"debug@test.com\", \"nombre\": \"Voluntario Debug\", \"telefono\": \"123456789\"}',NULL,NULL),(48,42,11,'2025-10-12 22:38:44','CANCELADA','{\"name\": \"Juan\", \"email\": \"admin@empujecomunitario.org\", \"phone\": \"\", \"surname\": \"Pérez\"}','2025-10-12 22:38:54',NULL),(49,43,11,'2025-10-12 22:40:01','CANCELADA','{\"name\": \"Juan\", \"email\": \"admin@empujecomunitario.org\", \"phone\": \"\", \"surname\": \"Pérez\"}','2025-10-12 22:40:09',NULL),(50,44,17,'2025-10-12 22:43:03','CANCELADA','{\"email\": \"maria@esperanza.org\", \"nombre\": \"María González\", \"telefono\": \"123456789\"}',NULL,NULL),(51,45,17,'2025-10-13 00:27:39','CANCELADA','{\"name\": \"María\", \"email\": \"maria@esperanza.org\", \"phone\": \"\", \"surname\": \"González\"}','2025-10-13 00:28:53',NULL),(52,48,11,'2025-10-23 15:30:40','CONFIRMADA','{\"name\": \"Juan\", \"email\": \"admin@empujecomunitario.org\", \"phone\": \"\", \"surname\": \"Pérez\"}','2025-10-23 15:31:26',NULL),(53,48,14,'2025-10-23 17:31:40','CONFIRMADA','{\"name\": \"AnaSAT\", \"email\": \"ana@empujecomunitario.org\", \"phone\": \"\", \"surname\": \"Martínez\"}','2025-10-23 17:31:57',NULL);
/*!40000 ALTER TABLE `adhesiones_eventos_externos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `archivos_excel`
--

DROP TABLE IF EXISTS `archivos_excel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `archivos_excel` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `usuario_id` int NOT NULL,
  `nombre_archivo` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ruta_archivo` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_creacion` datetime DEFAULT NULL,
  `fecha_expiracion` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `archivos_excel_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `archivos_excel`
--

LOCK TABLES `archivos_excel` WRITE;
/*!40000 ALTER TABLE `archivos_excel` DISABLE KEYS */;
INSERT INTO `archivos_excel` VALUES ('1546a750-d78e-498a-8532-2938f8dc0164',11,'reporte_transferencias_tipo_enviada_desde_20240101_hasta_20241231_20251026_175059.xlsx','./storage/excel\\1f29ee43-e9b6-4778-bcd8-db41cfd86306_reporte_transferencias_tipo_enviada_desde_20240101_hasta_20241231_20251026_175059.xlsx','2025-10-26 20:51:00','2025-10-27 20:51:00'),('2714c309-b2c6-4710-b933-bd907c414e61',11,'reporte_transferencias_tipo_enviada_desde_20240101_hasta_20241231_20251026_171854.xlsx','./storage/excel\\0a81c0b8-295a-4bae-806b-e643d7654964_reporte_transferencias_tipo_enviada_desde_20240101_hasta_20241231_20251026_171854.xlsx','2025-10-26 20:18:55','2025-10-27 20:18:55'),('464eec3d-21fa-455e-abbe-73701a2a963e',11,'reporte_donaciones_categoria_ropa_desde_20251001_hasta_20251031_20251026_162403.xlsx','./storage/excel\\2a127a71-cf4c-4fdf-a428-e565c148a506_reporte_donaciones_categoria_ropa_desde_20251001_hasta_20251031_20251026_162403.xlsx','2025-10-26 19:24:04','2025-10-27 19:24:04'),('5aa26903-f34d-4cbb-b7ed-cfdec6d69fbc',11,'reporte_donaciones_20251026_162158.xlsx','./storage/excel\\7218b881-ca1e-491e-82f5-bc4bf1bec0eb_reporte_donaciones_20251026_162158.xlsx','2025-10-26 19:21:59','2025-10-27 19:21:59'),('6bc7c164-8fa3-4b17-b184-83c65c0250eb',11,'reporte_donaciones_categoria_alimentos_desde_20240101_hasta_20241231_20251026_175520.xlsx','./storage/excel\\e39f5174-e185-4559-965b-26193b33eaf3_reporte_donaciones_categoria_alimentos_desde_20240101_hasta_20241231_20251026_175520.xlsx','2025-10-26 20:55:21','2025-10-27 20:55:21'),('7af8e634-75c0-4eee-880b-4bdade52f991',11,'reporte_transferencias_tipo_enviada_desde_20240101_hasta_20241231_20251026_171853.xlsx','./storage/excel\\6891cddc-de75-4d5d-aa1a-077042a27646_reporte_transferencias_tipo_enviada_desde_20240101_hasta_20241231_20251026_171853.xlsx','2025-10-26 20:18:54','2025-10-27 20:18:54'),('86265e70-1f24-47d4-9bf1-1101c60cae2d',11,'reporte_donaciones_20251026_193459.xlsx','./storage/excel\\7cb8bb32-bec2-4c96-b467-5b3979fe214b_reporte_donaciones_20251026_193459.xlsx','2025-10-26 22:35:00','2025-10-27 22:35:00'),('8a911ed0-6f1f-4799-b403-5d4e0e3160cf',11,'reporte_transferencias_tipo_enviada_desde_20240101_hasta_20241231_20251026_171850.xlsx','./storage/excel\\5d1e5281-caee-4faa-ad1b-d141e27939eb_reporte_transferencias_tipo_enviada_desde_20240101_hasta_20241231_20251026_171850.xlsx','2025-10-26 20:18:50','2025-10-27 20:18:50'),('ae2fe361-c0d6-4c7d-96f3-a855ccf5b5d9',11,'reporte_donaciones_categoria_alimentos_desde_20240101_hasta_20241231_20251026_171836.xlsx','./storage/excel\\5b279c06-cc0c-4982-a3c9-63e8929584ce_reporte_donaciones_categoria_alimentos_desde_20240101_hasta_20241231_20251026_171836.xlsx','2025-10-26 20:18:36','2025-10-27 20:18:36'),('e984c5c1-df13-4c2e-b865-a377b20037ec',11,'reporte_donaciones_categoria_alimentos_desde_20240101_hasta_20241231_20251026_175056.xlsx','./storage/excel\\6a4ae8b8-f338-4adf-bb4c-1b84620bd69d_reporte_donaciones_categoria_alimentos_desde_20240101_hasta_20241231_20251026_175056.xlsx','2025-10-26 20:50:57','2025-10-27 20:50:57'),('f6070f2d-c221-4bf0-b99f-0fb73e9d5677',11,'reporte_transferencias_tipo_enviada_desde_20251001_hasta_20251031_20251026_190837.xlsx','./storage/excel\\3781ae5c-777c-479d-9e10-079fe3fd344e_reporte_transferencias_tipo_enviada_desde_20251001_hasta_20251031_20251026_190837.xlsx','2025-10-26 22:08:38','2025-10-27 22:08:38');
/*!40000 ALTER TABLE `archivos_excel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `configuracion_organizacion`
--

DROP TABLE IF EXISTS `configuracion_organizacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `configuracion_organizacion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `clave` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `valor` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `clave` (`clave`),
  KEY `idx_configuracion_clave` (`clave`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `configuracion_organizacion`
--

LOCK TABLES `configuracion_organizacion` WRITE;
/*!40000 ALTER TABLE `configuracion_organizacion` DISABLE KEYS */;
INSERT INTO `configuracion_organizacion` VALUES (1,'ORGANIZATION_ID','empuje-comunitario','Identificador único de la organización en la red de ONGs','2025-09-30 21:42:44','2025-09-30 21:42:44'),(2,'KAFKA_ENABLED','true','Habilitar funcionalidades de mensajería Kafka','2025-09-30 21:42:44','2025-09-30 21:42:44'),(3,'AUTO_PROCESS_EXTERNAL_REQUESTS','true','Procesar automáticamente solicitudes externas','2025-09-30 21:42:44','2025-09-30 21:42:44'),(4,'MAX_TRANSFER_AMOUNT','1000','Cantidad máxima permitida para transferencias automáticas','2025-09-30 21:42:44','2025-09-30 21:42:44');
/*!40000 ALTER TABLE `configuracion_organizacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `donaciones`
--

DROP TABLE IF EXISTS `donaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `donaciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `categoria` enum('ROPA','ALIMENTOS','JUGUETES','UTILES_ESCOLARES') COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `cantidad` int NOT NULL,
  `eliminado` tinyint(1) DEFAULT '0',
  `fecha_alta` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `usuario_alta` int DEFAULT NULL,
  `fecha_modificacion` timestamp NULL DEFAULT NULL,
  `usuario_modificacion` int DEFAULT NULL,
  `organizacion` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT 'empuje-comunitario',
  PRIMARY KEY (`id`),
  KEY `usuario_alta` (`usuario_alta`),
  KEY `usuario_modificacion` (`usuario_modificacion`),
  CONSTRAINT `donaciones_ibfk_1` FOREIGN KEY (`usuario_alta`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `donaciones_ibfk_2` FOREIGN KEY (`usuario_modificacion`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `donaciones_chk_1` CHECK ((`cantidad` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `donaciones`
--

LOCK TABLES `donaciones` WRITE;
/*!40000 ALTER TABLE `donaciones` DISABLE KEYS */;
INSERT INTO `donaciones` VALUES (2,'ALIMENTOS','Puré de tomates en lata',39,1,'2025-09-30 14:17:10',1,'2025-09-30 18:31:40',11,'empuje-comunitario'),(3,'ALIMENTOS','Arroz blanco 1kg',35,1,'2025-09-30 14:17:10',1,'2025-09-30 23:17:53',11,'empuje-comunitario'),(4,'ROPA','Camisetas talle M',45,0,'2025-09-30 14:17:10',2,'2025-10-01 16:38:01',17,'empuje-comunitario'),(5,'ROPA','Pantalones infantiles',20,0,'2025-09-30 14:17:10',2,NULL,NULL,'empuje-comunitario'),(6,'JUGUETES','Pelotas de fútbol',15,0,'2025-09-30 14:17:10',1,NULL,NULL,'empuje-comunitario'),(7,'JUGUETES','Muñecas de trapo',5,0,'2025-09-30 14:17:10',2,NULL,NULL,'empuje-comunitario'),(8,'UTILES_ESCOLARES','Cuadernos rayados',100,0,'2025-09-30 14:17:10',1,NULL,NULL,'empuje-comunitario'),(9,'UTILES_ESCOLARES','Lápices de colores',44,0,'2025-09-30 14:17:10',2,NULL,NULL,'empuje-comunitario'),(10,'ROPA','Ropa para donación',1,1,'2025-09-30 14:36:32',11,'2025-09-30 14:44:44',11,'empuje-comunitario'),(11,'ROPA','Ropa para donación',1,1,'2025-09-30 15:06:14',11,'2025-09-30 15:06:17',11,'empuje-comunitario'),(17,'ALIMENTOS','Alimentos no perecederos',5,0,'2025-10-02 00:01:48',11,NULL,NULL,'empuje-comunitario'),(19,'ALIMENTOS','Alimentos no perecederos',4,0,'2025-10-02 00:02:37',11,NULL,NULL,'empuje-comunitario'),(21,'ALIMENTOS','Alimentos no perecederos',5,0,'2025-10-02 00:04:18',11,NULL,NULL,'empuje-comunitario'),(22,'ALIMENTOS','Alimentos no perecederos',2,0,'2025-10-02 00:04:31',11,'2025-10-12 22:51:14',11,'empuje-comunitario'),(24,'ALIMENTOS','Arroz para familias',5,0,'2025-10-02 00:13:04',17,NULL,NULL,'fundacion-esperanza'),(26,'ALIMENTOS','Juguetes navideños',130,0,'2025-10-02 00:13:04',18,'2025-10-05 22:50:59',17,'fundacion-esperanza'),(27,'ALIMENTOS','Leche en polvo',8,0,'2025-10-02 00:13:04',19,NULL,NULL,'ong-solidaria'),(28,'UTILES_ESCOLARES','Cuadernos y lápices',20,0,'2025-10-02 00:13:04',20,NULL,NULL,'ong-solidaria'),(29,'ROPA','Zapatos usados',12,0,'2025-10-02 00:13:04',21,NULL,NULL,'centro-comunitario'),(30,'ALIMENTOS','Conservas variadas',6,0,'2025-10-02 00:13:04',22,NULL,NULL,'centro-comunitario'),(37,'ALIMENTOS','Alimentos no perecederos',43,0,'2025-10-02 00:25:47',17,'2025-10-26 22:31:56',11,'empuje-comunitario'),(39,'ALIMENTOS','Alimentos no perecederos',10,0,'2025-10-12 23:15:42',17,NULL,NULL,'esperanza-social'),(40,'ROPA','Ropa para donación',15,0,'2025-10-12 23:15:42',17,NULL,NULL,'esperanza-social'),(44,'ALIMENTOS','Arroz, fideos, aceite',40,0,'2025-10-23 17:45:41',14,'2025-10-26 22:30:46',11,'empuje-comunitario'),(45,'ROPA','Camperas y abrigos',20,0,'2025-10-23 17:46:17',14,'2025-10-26 22:30:45',11,'empuje-comunitario');
/*!40000 ALTER TABLE `donaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `donaciones_repartidas`
--

DROP TABLE IF EXISTS `donaciones_repartidas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `donaciones_repartidas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `evento_id` int DEFAULT NULL,
  `donacion_id` int DEFAULT NULL,
  `cantidad_repartida` int NOT NULL,
  `usuario_registro` int DEFAULT NULL,
  `fecha_registro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `evento_id` (`evento_id`),
  KEY `donacion_id` (`donacion_id`),
  KEY `usuario_registro` (`usuario_registro`),
  CONSTRAINT `donaciones_repartidas_ibfk_1` FOREIGN KEY (`evento_id`) REFERENCES `eventos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `donaciones_repartidas_ibfk_2` FOREIGN KEY (`donacion_id`) REFERENCES `donaciones` (`id`),
  CONSTRAINT `donaciones_repartidas_ibfk_3` FOREIGN KEY (`usuario_registro`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `donaciones_repartidas_chk_1` CHECK ((`cantidad_repartida` > 0))
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `donaciones_repartidas`
--

LOCK TABLES `donaciones_repartidas` WRITE;
/*!40000 ALTER TABLE `donaciones_repartidas` DISABLE KEYS */;
INSERT INTO `donaciones_repartidas` VALUES (7,24,37,15,11,'2025-10-12 22:51:14'),(9,24,22,3,11,'2025-10-12 22:51:14'),(11,51,44,50,14,'2025-10-23 17:45:41'),(12,53,45,30,14,'2025-10-23 17:46:17'),(18,58,45,10,11,'2025-10-26 22:30:45'),(19,58,44,10,11,'2025-10-26 22:30:46'),(20,58,37,10,11,'2025-10-26 22:30:46'),(21,57,37,25,11,'2025-10-26 22:31:56');
/*!40000 ALTER TABLE `donaciones_repartidas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eventos`
--

DROP TABLE IF EXISTS `eventos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eventos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `fecha_evento` timestamp NOT NULL,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `expuesto_red` tinyint(1) DEFAULT '0',
  `organizacion` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT 'empuje-comunitario',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eventos`
--

LOCK TABLES `eventos` WRITE;
/*!40000 ALTER TABLE `eventos` DISABLE KEYS */;
INSERT INTO `eventos` VALUES (13,'adm_dashboard','testr','2025-10-04 23:47:00','2025-09-30 23:47:13','2025-10-01 16:48:51',0,'empuje-comunitario'),(22,'test terminado','test','2025-10-07 01:27:00','2025-10-06 01:27:07','2025-10-06 01:27:29',1,'empuje-comunitario'),(24,'test nuevo eventop','asd123','2025-10-12 21:37:00','2025-10-11 21:37:37','2025-10-11 21:54:59',0,'empuje-comunitario'),(30,'Evento de Prueba Cancelación - 19:07:45','Evento creado para probar notificaciones de cancelación','2025-10-19 22:07:45','2025-10-12 22:07:45','2025-10-12 22:07:45',0,'esperanza-social'),(38,'Evento Fresh Test - 19:26:10','Evento para test fresco','2025-10-19 22:26:11','2025-10-12 22:26:10','2025-10-12 22:26:10',1,'esperanza-social'),(39,'Evento Fresh Test - 19:27:33','Evento para test fresco','2025-10-19 22:27:33','2025-10-12 22:27:33','2025-10-12 22:27:33',1,'esperanza-social'),(40,'Evento Fresh Test - 19:30:43','Evento para test fresco','2025-10-19 22:30:43','2025-10-12 22:30:43','2025-10-12 22:30:43',1,'esperanza-social'),(44,'Evento Hide Test - 19:43:02','Evento para probar ocultar de la red','2025-10-19 22:43:03','2025-10-12 22:43:03','2025-10-12 22:43:03',0,'esperanza-social'),(47,'test evemt','tester','2025-11-02 02:00:00','2025-10-22 02:00:47','2025-10-22 02:00:47',0,'empuje-comunitario'),(48,'Intercambio y entrega de ropa','','2025-10-24 15:22:00','2025-10-23 15:30:31','2025-10-23 15:30:34',1,'fundacion-esperanza'),(51,'Entrega de Alimentos - Septiembre','Distribución mensual de alimentos a familias necesitadas','2024-09-15 13:00:00','2025-10-23 17:45:41','2025-10-23 17:45:41',0,'empuje-comunitario'),(52,'Jornada de Juegos - Septiembre','Actividades recreativas para niños del barrio','2024-09-22 17:00:00','2025-10-23 17:46:17','2025-10-23 17:46:17',0,'empuje-comunitario'),(53,'Entrega de Ropa - Octubre','Distribución de ropa de invierno','2024-10-10 12:00:00','2025-10-23 17:46:17','2025-10-23 17:46:17',0,'empuje-comunitario'),(54,'Taller de Manualidades - Octubre','Taller de manualidades para adultos mayores','2024-10-25 18:00:00','2025-10-23 17:46:17','2025-10-23 17:46:17',0,'empuje-comunitario'),(55,'Celebración Día del Niño','Festejo especial con juegos y regalos','2024-11-20 19:00:00','2025-10-23 17:46:17','2025-10-23 17:46:17',0,'empuje-comunitario'),(56,'Entrega de Útiles - Noviembre','Distribución de útiles escolares','2024-11-30 13:00:00','2025-10-23 17:46:17','2025-10-23 17:46:17',0,'empuje-comunitario'),(57,'Inicio de Clases 2025','Apoyo para el inicio del ciclo lectivo','2025-01-15 11:00:00','2025-10-23 17:46:17','2025-10-23 17:46:17',0,'empuje-comunitario'),(58,'Jornada de Salud Comunitaria','Controles de salud gratuitos','2025-01-25 12:00:00','2025-10-23 17:46:17','2025-10-23 17:46:17',0,'empuje-comunitario');
/*!40000 ALTER TABLE `eventos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eventos_red`
--

DROP TABLE IF EXISTS `eventos_red`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eventos_red` (
  `id` int NOT NULL AUTO_INCREMENT,
  `evento_id` int NOT NULL,
  `organizacion_origen` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `fecha_evento` datetime NOT NULL,
  `fecha_publicacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `evento_id` (`evento_id`,`organizacion_origen`),
  KEY `idx_eventos_red_organizacion` (`organizacion_origen`),
  KEY `idx_eventos_red_activo` (`activo`),
  KEY `idx_eventos_red_fecha` (`fecha_evento`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eventos_red`
--

LOCK TABLES `eventos_red` WRITE;
/*!40000 ALTER TABLE `eventos_red` DISABLE KEYS */;
INSERT INTO `eventos_red` VALUES (7,13,'empuje-comunitario','adm_dashboard','testr','2025-10-04 20:47:00','2025-10-01 00:08:23',0),(21,20,'empuje-comunitario','orgCom','test','2025-10-18 21:23:00','2025-10-11 17:19:50',0),(22,21,'fundacion-esperanza','eventEsp','test','2025-10-24 21:24:00','2025-10-11 21:55:20',0),(24,22,'empuje-comunitario','test terminado','test','2025-10-06 22:27:00','2025-10-06 01:27:29',1),(27,23,'empuje-comunitario','test','tester','2025-10-25 22:49:00','2025-10-06 01:49:24',1),(30,24,'empuje-comunitario','test nuevo eventop','asd123','2025-10-12 18:37:00','2025-10-11 21:38:11',0),(32,25,'fundacion-esperanza','TEST','test','2025-10-19 20:45:00','2025-10-11 23:58:03',0),(34,26,'fundacion-esperanza','tEST2','TEST','2025-10-18 20:58:00','2025-10-11 23:58:25',1),(35,27,'fundacion-esperanza','test eliminar','test','2025-10-16 16:28:00','2025-10-12 19:39:15',1),(37,28,'fundacion-esperanza','test2','tst','2025-10-19 16:40:00','2025-10-12 19:40:11',1),(38,29,'fundacion-esperanza','Test3','event test','2025-10-25 18:56:00','2025-10-12 21:56:29',1),(39,32,'esperanza-social','Evento Cancelación Test - 19:11:41','Evento creado para probar notificaciones de cancelación','2025-10-19 19:11:42','2025-10-12 22:11:41',0),(40,33,'fundacion-esperanza','test3','tester','2025-10-31 19:21:00','2025-10-12 22:22:17',1),(42,34,'esperanza-social','Evento Debug Eliminación - 19:22:33','Evento para debuggear eliminación','2025-10-19 19:22:34','2025-10-12 22:22:34',1),(43,35,'esperanza-social','Evento Debug Eliminación - 19:23:36','Evento para debuggear eliminación','2025-10-19 19:23:36','2025-10-12 22:23:36',1),(44,36,'esperanza-social','Evento Debug Eliminación - 19:24:21','Evento para debuggear eliminación','2025-10-19 19:24:21','2025-10-12 22:24:21',1),(45,37,'esperanza-social','Evento Debug Eliminación - 19:25:04','Evento para debuggear eliminación','2025-10-19 19:25:05','2025-10-12 22:25:04',1),(46,38,'esperanza-social','Evento Fresh Test - 19:26:10','Evento para test fresco','2025-10-19 19:26:11','2025-10-12 22:26:10',1),(47,39,'esperanza-social','Evento Fresh Test - 19:27:33','Evento para test fresco','2025-10-19 19:27:33','2025-10-12 22:27:33',1),(48,40,'esperanza-social','Evento Fresh Test - 19:30:43','Evento para test fresco','2025-10-19 19:30:43','2025-10-12 22:30:43',1),(49,41,'esperanza-social','Evento Debug Eliminación - 19:33:33','Evento para debuggear eliminación','2025-10-19 19:33:34','2025-10-12 22:33:33',1),(50,42,'fundacion-esperanza','Hospital Salud','Test','2025-11-09 19:38:00','2025-10-12 22:39:13',1),(52,43,'fundacion-esperanza','Test test','test','2025-10-17 19:39:00','2025-10-12 22:50:03',1),(53,44,'esperanza-social','Evento Hide Test - 19:43:02','Evento para probar ocultar de la red','2025-10-19 19:43:03','2025-10-12 22:43:03',0),(57,45,'empuje-comunitario','Evento PRUEBA','evento de prueba','2025-10-25 21:25:00','2025-10-13 00:26:14',1),(58,46,'empuje-comunitario','test','asd','2025-10-24 20:48:00','2025-10-21 23:48:18',1),(59,48,'fundacion-esperanza','Intercambio y entrega de ropa','','2025-10-24 12:22:00','2025-10-23 15:30:34',1);
/*!40000 ALTER TABLE `eventos_red` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `filtros_guardados`
--

DROP TABLE IF EXISTS `filtros_guardados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `filtros_guardados` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `nombre` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tipo` enum('DONACIONES','EVENTOS') COLLATE utf8mb4_unicode_ci NOT NULL,
  `configuracion` json NOT NULL,
  `fecha_creacion` datetime DEFAULT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `filtros_guardados_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `filtros_guardados`
--

LOCK TABLES `filtros_guardados` WRITE;
/*!40000 ALTER TABLE `filtros_guardados` DISABLE KEYS */;
INSERT INTO `filtros_guardados` VALUES (8,17,'ropa','DONACIONES','{\"categoria\": \"ROPA\"}','2025-10-23 17:04:25','2025-10-23 17:04:25'),(10,11,'Eventos vol1 2024','EVENTOS','{\"usuario_id\": 14, \"fecha_desde\": \"2024-01-01\", \"fecha_hasta\": \"2024-12-31\", \"repartodonaciones\": true}','2025-10-23 19:13:57','2025-10-23 19:13:57'),(12,11,'Eventos vol1 2024','EVENTOS','{\"usuario_id\": 14, \"fecha_desde\": \"2024-01-01\", \"fecha_hasta\": \"2024-12-31\", \"repartodonaciones\": true}','2025-10-23 19:14:18','2025-10-23 19:14:18'),(14,11,'Eventos vol1 2024','EVENTOS','{\"usuario_id\": 14, \"fecha_desde\": \"2024-01-01\", \"fecha_hasta\": \"2024-12-31\", \"repartodonaciones\": true}','2025-10-23 19:14:54','2025-10-23 19:14:54'),(24,11,'test','EVENTOS','{\"usuario_id\": 0, \"fecha_desde\": \"2025-02-23\", \"fecha_hasta\": null, \"filter_subtype\": \"EVENT\", \"repartodonaciones\": true}','2025-10-23 20:02:40','2025-10-23 20:02:40'),(25,14,'General - Con donaciones','EVENTOS','{\"usuario_id\": 14, \"fecha_desde\": null, \"fecha_hasta\": null, \"filter_subtype\": \"EVENT\", \"repartodonaciones\": true}','2025-10-26 19:51:03','2025-10-26 19:51:03'),(28,11,'Test filter','DONACIONES','{\"categoria\": \"ALIMENTOS\", \"eliminado\": false}','2025-10-26 22:34:33','2025-10-26 22:34:33'),(29,11,'Test','EVENTOS','{\"usuario_id\": 0, \"fecha_desde\": \"2025-07-26\", \"fecha_hasta\": null, \"filter_subtype\": \"EVENT\", \"repartodonaciones\": false}','2025-10-26 22:49:00','2025-10-26 22:49:00');
/*!40000 ALTER TABLE `filtros_guardados` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial_mensajes`
--

DROP TABLE IF EXISTS `historial_mensajes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_mensajes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `topic` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tipo_mensaje` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mensaje_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `organizacion_origen` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `organizacion_destino` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contenido` json NOT NULL,
  `estado` enum('PROCESADO','ERROR','PENDIENTE') COLLATE utf8mb4_unicode_ci DEFAULT 'PROCESADO',
  `fecha_procesamiento` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `error_detalle` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `idx_historial_topic` (`topic`),
  KEY `idx_historial_tipo` (`tipo_mensaje`),
  KEY `idx_historial_fecha` (`fecha_procesamiento`),
  KEY `idx_historial_estado` (`estado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial_mensajes`
--

LOCK TABLES `historial_mensajes` WRITE;
/*!40000 ALTER TABLE `historial_mensajes` DISABLE KEYS */;
/*!40000 ALTER TABLE `historial_mensajes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notificaciones`
--

DROP TABLE IF EXISTS `notificaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notificaciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `tipo` enum('transferencia_recibida','transferencia_enviada','adhesion_evento','solicitud_donacion','evento_cancelado','inscripcion_procesada') COLLATE utf8mb4_unicode_ci NOT NULL,
  `titulo` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mensaje` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `datos_adicionales` json DEFAULT NULL,
  `leida` tinyint(1) DEFAULT '0',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_lectura` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_notificaciones_usuario` (`usuario_id`),
  KEY `idx_notificaciones_tipo` (`tipo`),
  KEY `idx_notificaciones_leida` (`leida`),
  KEY `idx_notificaciones_fecha` (`fecha_creacion`),
  CONSTRAINT `notificaciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notificaciones`
--

LOCK TABLES `notificaciones` WRITE;
/*!40000 ALTER TABLE `notificaciones` DISABLE KEYS */;
INSERT INTO `notificaciones` VALUES (3,26,'transferencia_recibida','? ¡Donación recibida!','Has recibido una transferencia manual de prueba de Empuje Comunitario','{\"request_id\": \"manual-test-request\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',0,'2025-10-12 17:56:59',NULL),(4,11,'transferencia_enviada','? Donación enviada','Has enviado donaciones a Esperanza Social exitosamente. Las donaciones han sido entregadas.','{\"request_id\": \"simulated-request-001\", \"cantidad_items\": 1, \"organizacion_destino\": \"esperanza-social\"}',1,'2025-10-12 18:04:11','2025-10-12 22:21:03'),(5,26,'transferencia_recibida','? ¡Donación recibida!','Has recibido donaciones de Empuje Comunitario. Las donaciones ya están disponibles en tu inventario.','{\"request_id\": \"simulated-request-001\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',0,'2025-10-12 18:04:11',NULL),(6,11,'transferencia_enviada','? Donación enviada exitosamente','Has enviado 5 kg de Arroz blanco premium a Esperanza Social. La transferencia se completó correctamente.','{\"request_id\": \"fix-request-1760293876\", \"transfer_id\": \"fix-44\", \"cantidad_items\": 1, \"organizacion_destino\": \"esperanza-social\"}',1,'2025-10-12 18:31:16','2025-10-12 19:24:39'),(7,26,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de Empuje Comunitario:\n\n• Arroz blanco premium (5 kg)\n\nLas donaciones ya están disponibles en tu inventario. ¡Gracias por formar parte de la red de colaboración!','{\"request_id\": \"fix-request-1760293876\", \"transfer_id\": \"fix-45\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',0,'2025-10-12 18:31:16',NULL),(8,26,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de empuje-comunitario:\n\n• Prueba de donación multi-org (1)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"real-test-1760294648\", \"transfer_id\": \"simulated-49\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',0,'2025-10-12 18:44:50',NULL),(9,26,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de empuje-comunitario:\n\n• Prueba de donación multi-org (1)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"real-test-1760294592\", \"transfer_id\": \"simulated-48\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',0,'2025-10-12 18:44:50',NULL),(10,26,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de empuje-comunitario:\n\n• Prueba de donación multi-org (1)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"real-test-1760294548\", \"transfer_id\": \"simulated-47\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',0,'2025-10-12 18:44:50',NULL),(11,26,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de empuje-comunitario:\n\n• Prueba de donación multi-org (1)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"req-esperanza-social-b24b5592\", \"transfer_id\": \"simulated-46\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',0,'2025-10-12 18:44:50',NULL),(12,26,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de empuje-comunitario:\n\n• Prueba de donación multi-org (1)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"real-test-1760293773\", \"transfer_id\": \"simulated-43\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',0,'2025-10-12 18:44:50',NULL),(13,26,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de empuje-comunitario:\n\n• Prueba de donación multi-org (1)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"real-test-1760293619\", \"transfer_id\": \"simulated-42\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',0,'2025-10-12 18:44:50',NULL),(14,26,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de empuje-comunitario:\n\n• Lápices de colores (1)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"req-esperanza-social-b24b5592\", \"transfer_id\": \"simulated-41\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',0,'2025-10-12 18:44:50',NULL),(15,26,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de empuje-comunitario:\n\n• Prueba de donación multi-org (1)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"direct-test-1760292150\", \"transfer_id\": \"simulated-38\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',0,'2025-10-12 18:44:50',NULL),(16,26,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de empuje-comunitario:\n\n• Prueba de donación multi-org (3)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"direct-test-1760291686\", \"transfer_id\": \"simulated-36\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',0,'2025-10-12 18:44:50',NULL),(17,26,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de empuje-comunitario:\n\n• asdasd esese (1)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"req-esperanza-social-b24b5592\", \"transfer_id\": \"transfer-empuje-comunitario-54c7d29a\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',0,'2025-10-12 18:50:28',NULL),(18,26,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de empuje-comunitario:\n\n• Test automatización (1)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"test-auto-1760295751\", \"transfer_id\": \"auto-61\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',0,'2025-10-12 19:02:31',NULL),(19,26,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de empuje-comunitario:\n\n• Test API directo (1)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"api-test-1760295817\", \"transfer_id\": \"auto-63\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',0,'2025-10-12 19:03:37',NULL),(20,26,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de empuje-comunitario:\n\n• Test automatización completa (3)\n• Camisetas para niños (2)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"complete-test-1760295862\", \"transfer_id\": \"auto-65\", \"cantidad_items\": 2, \"organizacion_origen\": \"empuje-comunitario\"}',0,'2025-10-12 19:04:22',NULL),(21,17,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de empuje-comunitario:\n\n• Lápices de colores (5)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"req-fundacion-esperanza-213032a4\", \"transfer_id\": \"auto-69\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',1,'2025-10-12 19:26:46','2025-10-12 19:26:53'),(22,18,'adhesion_evento','? Nueva solicitud de adhesión a evento','Test Notification 1760298294 quiere participar en tu evento \'test eliminar\'. Revisa la solicitud en la sección de adhesiones.',NULL,0,'2025-10-12 19:44:54',NULL),(23,26,'adhesion_evento','✅ Adhesión a evento aprobada','¡Genial! Tu solicitud para participar en \'test eliminar\' ha sido aprobada. ¡Nos vemos en el evento!',NULL,0,'2025-10-12 19:44:55',NULL),(24,17,'solicitud_donacion','? Solicitud de contacto por oferta','esperanza-social está interesada en su oferta de donaciones (ID: OFE-2025-001). Mensaje: Estamos muy interesados en coordinar la obtención de estas donaciones para nuestros beneficiarios.',NULL,1,'2025-10-12 20:41:01','2025-10-12 22:37:09'),(25,26,'solicitud_donacion','✅ Solicitud de contacto enviada','Hemos notificado a fundacion-esperanza sobre su interés en la oferta OFE-2025-001. Deberían contactarlos pronto para coordinar la obtención de las donaciones.',NULL,0,'2025-10-12 20:41:01',NULL),(26,17,'solicitud_donacion','? Solicitud de contacto por oferta','esperanza-social está interesada en su oferta de donaciones (ID: OFE-2025-001). Mensaje: Hola! Somos de Esperanza Social y estamos muy interesados en coordinar la obtención de las donaciones de su oferta OFE-2025-001. Tenemos capacidad para recoger las donaciones esta semana y distribuirlas inmediatamente a nuestros beneficiarios. ¿Podrían contactarnos para coordinar los detalles? Muchas gracias por su solidaridad.',NULL,1,'2025-10-12 20:51:15','2025-10-12 22:37:09'),(27,26,'solicitud_donacion','✅ Solicitud de contacto enviada','Hemos notificado a fundacion-esperanza sobre su interés en la oferta OFE-2025-001. Deberían contactarlos pronto para coordinar la obtención de las donaciones.',NULL,0,'2025-10-12 20:51:15',NULL),(28,17,'solicitud_donacion','? Solicitud de contacto por oferta','fundacion-esperanza está interesada en su oferta de donaciones (ID: OFE-2025-001). Mensaje: Estamos interesados en coordinar la obtención de las donaciones de su oferta. Nos gustaría establecer contacto para discutir los detalles de la transferencia. gracas',NULL,1,'2025-10-12 20:52:39','2025-10-12 20:52:58'),(29,17,'solicitud_donacion','✅ Solicitud de contacto enviada','Hemos notificado a fundacion-esperanza sobre su interés en la oferta OFE-2025-001. Deberían contactarlos pronto para coordinar la obtención de las donaciones.',NULL,1,'2025-10-12 20:52:39','2025-10-12 22:37:09'),(30,17,'solicitud_donacion','? Solicitud de contacto por oferta','esperanza-social está interesada en su oferta de donaciones (ID: OFE-2025-001). Mensaje: Mensaje enviado desde el modal elegante sin popups de JavaScript. Estamos interesados en coordinar la obtención de estas donaciones para nuestros beneficiarios. Por favor contactarnos para coordinar los detalles.',NULL,1,'2025-10-12 20:55:00','2025-10-12 22:37:09'),(31,26,'solicitud_donacion','✅ Solicitud de contacto enviada','Hemos notificado a fundacion-esperanza sobre su interés en la oferta OFE-2025-001. Deberían contactarlos pronto para coordinar la obtención de las donaciones.',NULL,0,'2025-10-12 20:55:00',NULL),(32,17,'solicitud_donacion','? Solicitud de contacto por oferta','empuje-comunitario está interesada en su oferta de donaciones (ID: OFE-2025-001). Mensaje: Estamos interesados en coordinar la obtención de las donaciones de su oferta. Nos gustaría establecer contacto para discutir los detalles de la transferencia.',NULL,1,'2025-10-12 20:57:09','2025-10-12 22:37:09'),(33,11,'solicitud_donacion','✅ Solicitud de contacto enviada','Hemos notificado a fundacion-esperanza sobre su interés en la oferta OFE-2025-001. Deberían contactarlos pronto para coordinar la obtención de las donaciones.',NULL,1,'2025-10-12 20:57:09','2025-10-12 22:21:03'),(34,26,'adhesion_evento','? Nueva solicitud de adhesión a evento','María González quiere participar en tu evento \'Evento Cancelación Test - 19:11:41\'. Revisa la solicitud en la sección de adhesiones.',NULL,0,'2025-10-12 22:11:41',NULL),(35,17,'evento_cancelado','❌ Evento cancelado','Lamentamos informarte que el evento \"Evento Cancelación Test - 19:11:40\" de esperanza-social ha sido cancelado y removido de la red.\n\nTu adhesión ha sido automáticamente cancelada. Te notificaremos sobre futuros eventos similares.','{\"evento_id\": 32, \"evento_nombre\": \"Evento Cancelación Test - 19:11:40\", \"fecha_cancelacion\": \"2025-10-12T22:11:41.851Z\", \"organizacion_origen\": \"esperanza-social\"}',1,'2025-10-12 22:11:41','2025-10-12 22:37:09'),(36,17,'adhesion_evento','? Nueva solicitud de adhesión a evento','undefined quiere participar en tu evento \'Test3\'. Revisa la solicitud en la sección de adhesiones.',NULL,1,'2025-10-12 22:20:32','2025-10-12 22:20:36'),(37,11,'adhesion_evento','✅ Adhesión a evento aprobada','¡Genial! Tu solicitud para participar en \'Test3\' ha sido aprobada. ¡Nos vemos en el evento!',NULL,1,'2025-10-12 22:20:42','2025-10-12 22:20:55'),(38,17,'adhesion_evento','? Nueva solicitud de adhesión a evento','undefined quiere participar en tu evento \'test3\'. Revisa la solicitud en la sección de adhesiones.',NULL,1,'2025-10-12 22:22:08','2025-10-12 22:22:23'),(39,17,'evento_cancelado','? Test de notificación','Esta es una notificación de prueba para verificar que el servicio funciona correctamente.','{\"test\": true, \"timestamp\": \"2025-10-12T19:26:00Z\"}',1,'2025-10-12 22:27:08','2025-10-12 22:37:08'),(40,17,'adhesion_evento','? Nueva solicitud de adhesión a evento','undefined quiere participar en tu evento \'Hospital Salud\'. Revisa la solicitud en la sección de adhesiones.',NULL,1,'2025-10-12 22:38:44','2025-10-12 22:38:49'),(41,11,'adhesion_evento','✅ Adhesión a evento aprobada','¡Genial! Tu solicitud para participar en \'Hospital Salud\' ha sido aprobada. ¡Nos vemos en el evento!',NULL,1,'2025-10-12 22:38:54','2025-10-12 22:39:05'),(42,17,'adhesion_evento','? Nueva solicitud de adhesión a evento','undefined quiere participar en tu evento \'Test test\'. Revisa la solicitud en la sección de adhesiones.',NULL,1,'2025-10-12 22:40:01','2025-10-12 22:40:05'),(43,11,'adhesion_evento','✅ Adhesión a evento aprobada','¡Genial! Tu solicitud para participar en \'Test test\' ha sido aprobada. ¡Nos vemos en el evento!',NULL,1,'2025-10-12 22:40:09','2025-10-12 22:45:50'),(44,17,'evento_cancelado','❌ Evento cancelado','Lamentamos informarte que el evento \"Evento Hide Test - 19:43:02\" de esperanza-social ha sido cancelado y removido de la red.\n\nTu adhesión ha sido automáticamente cancelada. Te notificaremos sobre futuros eventos similares.','{\"evento_id\": 44, \"evento_nombre\": \"Evento Hide Test - 19:43:02\", \"fecha_cancelacion\": \"2025-10-12T22:43:03.174Z\", \"organizacion_origen\": \"esperanza-social\"}',1,'2025-10-12 22:43:03','2025-10-12 22:49:52'),(45,11,'evento_cancelado','❌ Evento cancelado','Lamentamos informarte que el evento \"Test test\" de fundacion-esperanza ha sido cancelado.\n\nTu adhesión ha sido automáticamente cancelada. Te notificaremos sobre futuros eventos similares.','{\"evento_id\": \"43\", \"evento_nombre\": \"Test test\", \"fecha_cancelacion\": \"2025-10-12T19:50:05.372420\", \"organizacion_origen\": \"fundacion-esperanza\"}',1,'2025-10-12 22:50:05','2025-10-12 22:50:08'),(46,11,'adhesion_evento','? Nueva solicitud de adhesión a evento','undefined quiere participar en tu evento \'Evento PRUEBA\'. Revisa la solicitud en la sección de adhesiones.',NULL,1,'2025-10-13 00:27:39','2025-10-21 20:35:09'),(47,17,'adhesion_evento','✅ Adhesión a evento aprobada','¡Genial! Tu solicitud para participar en \'Evento PRUEBA\' ha sido aprobada. ¡Nos vemos en el evento!',NULL,1,'2025-10-13 00:28:53','2025-10-23 15:20:05'),(48,17,'evento_cancelado','❌ Evento cancelado','Lamentamos informarte que el evento \"Evento PRUEBA\" de empuje-comunitario ha sido cancelado.\n\nTu adhesión ha sido automáticamente cancelada. Te notificaremos sobre futuros eventos similares.','{\"evento_id\": \"45\", \"evento_nombre\": \"Evento PRUEBA\", \"fecha_cancelacion\": \"2025-10-12T21:30:38.902199\", \"organizacion_origen\": \"empuje-comunitario\"}',1,'2025-10-13 00:30:38','2025-10-23 15:20:05'),(49,11,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de fundacion-esperanza:\n\n• Arroz para familias (5)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"req-empuje-comunitario-c9849c20\", \"transfer_id\": \"auto-71\", \"cantidad_items\": 1, \"organizacion_origen\": \"fundacion-esperanza\"}',1,'2025-10-13 00:33:19','2025-10-13 00:33:35'),(50,11,'solicitud_donacion','? Solicitud de contacto por oferta','fundacion-esperanza está interesada en su oferta de donaciones (ID: OFE-20251012-342b8b46). Mensaje: Estamos interesados en coordinar la obtención de las donaciones de su oferta. Nos gustaría establecer contacto para discutir los detalles de la transferencia.',NULL,1,'2025-10-13 00:35:49','2025-10-13 00:36:00'),(51,17,'solicitud_donacion','✅ Solicitud de contacto enviada','Hemos notificado a empuje-comunitario sobre su interés en la oferta OFE-20251012-342b8b46. Deberían contactarlos pronto para coordinar la obtención de las donaciones.',NULL,1,'2025-10-13 00:35:49','2025-10-23 15:20:05'),(52,17,'solicitud_donacion','? Solicitud de contacto por oferta','empuje-comunitario está interesada en su oferta de donaciones (ID: OFE-2025-001). Mensaje: Estamos interesados en coordinar la obtención de las donaciones de su oferta. Nos gustaría establecer contacto para discutir los detalles de la transferencia.',NULL,1,'2025-10-23 00:44:35','2025-10-23 15:20:05'),(53,11,'solicitud_donacion','✅ Solicitud de contacto enviada','Hemos notificado a fundacion-esperanza sobre su interés en la oferta OFE-2025-001. Deberían contactarlos pronto para coordinar la obtención de las donaciones.',NULL,1,'2025-10-23 00:44:35','2025-10-23 00:44:39'),(54,17,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de empuje-comunitario:\n\n• Prueba desde Node.js (5)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"req-fundacion-esperanza-9fa332d2\", \"transfer_id\": \"auto-74\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',1,'2025-10-23 15:19:57','2025-10-23 15:20:04'),(55,17,'adhesion_evento','? Nueva solicitud de adhesión a evento','undefined quiere participar en tu evento \'Intercambio y entrega de ropa\'. Revisa la solicitud en la sección de adhesiones.',NULL,1,'2025-10-23 15:30:40','2025-10-23 15:30:46'),(56,11,'adhesion_evento','✅ Adhesión a evento aprobada','¡Genial! Tu solicitud para participar en \'Intercambio y entrega de ropa\' ha sido aprobada. ¡Nos vemos en el evento!',NULL,1,'2025-10-23 15:31:26','2025-10-23 16:34:01'),(57,17,'transferencia_recibida','? ¡Nueva donación recibida!','Has recibido una donación de empuje-comunitario:\n\n• TEST ESPERANZA DIRECT (78)\n\nLas donaciones ya están disponibles en tu inventario.','{\"request_id\": \"req-fundacion-esperanza-7377a0e4\", \"transfer_id\": \"auto-80\", \"cantidad_items\": 1, \"organizacion_origen\": \"empuje-comunitario\"}',1,'2025-10-23 16:29:24','2025-10-23 16:30:05'),(58,17,'adhesion_evento','? Nueva solicitud de adhesión a evento','undefined quiere participar en tu evento \'Intercambio y entrega de ropa\'. Revisa la solicitud en la sección de adhesiones.',NULL,1,'2025-10-23 17:31:40','2025-10-23 17:31:47'),(59,14,'adhesion_evento','✅ Adhesión a evento aprobada','¡Genial! Tu solicitud para participar en \'Intercambio y entrega de ropa\' ha sido aprobada. ¡Nos vemos en el evento!',NULL,1,'2025-10-23 17:31:57','2025-10-23 19:34:31');
/*!40000 ALTER TABLE `notificaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notificaciones_usuarios`
--

DROP TABLE IF EXISTS `notificaciones_usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notificaciones_usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `titulo` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mensaje` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `tipo` enum('INFO','SUCCESS','WARNING','ERROR') COLLATE utf8mb4_unicode_ci DEFAULT 'INFO',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_leida` timestamp NULL DEFAULT NULL,
  `leida` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_notificaciones_usuario` (`usuario_id`),
  KEY `idx_notificaciones_leida` (`leida`),
  KEY `idx_notificaciones_fecha` (`fecha_creacion`),
  KEY `idx_notificaciones_tipo` (`tipo`),
  CONSTRAINT `notificaciones_usuarios_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Tabla de notificaciones para usuarios del sistema';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notificaciones_usuarios`
--

LOCK TABLES `notificaciones_usuarios` WRITE;
/*!40000 ALTER TABLE `notificaciones_usuarios` DISABLE KEYS */;
INSERT INTO `notificaciones_usuarios` VALUES (2,11,'Nueva adhesión a evento','Juan Pérez (fundacion-esperanza) quiere participar en \"Maratón Solidaria\". Revisa las adhesiones pendientes.','INFO','2025-10-11 23:02:05','2025-10-11 23:02:05',1),(3,11,'Adhesión aprobada','¡Genial! Tu solicitud para participar en \"Evento de Prueba\" ha sido aprobada. ¡Nos vemos en el evento!','SUCCESS','2025-10-11 23:02:05','2025-10-11 23:41:22',1),(4,11,'Evento cancelado','El evento \"Evento de Prueba\" ha sido cancelado. Motivo: Mal tiempo','ERROR','2025-10-11 23:02:05','2025-10-11 23:41:22',1),(5,11,'Donación recibida','Has recibido una donación de fundacion-esperanza: 10kg de alimentos','SUCCESS','2025-10-11 23:02:05','2025-10-11 23:41:22',1),(6,11,'Notificación para administradores','Esta es una notificación de prueba para todos los administradores de la organización.','INFO','2025-10-11 23:02:05','2025-10-11 23:41:22',1),(7,12,'Notificación para administradores','Esta es una notificación de prueba para todos los administradores de la organización.','INFO','2025-10-11 23:02:05',NULL,0),(8,11,'? Nueva adhesión a evento','María González (fundacion-esperanza) quiere participar en \"Maratón Solidaria\". Revisa las adhesiones pendientes para aprobar o rechazar.','INFO','2025-10-11 23:06:47','2025-10-11 23:40:50',1),(9,11,'✅ Adhesión aprobada','¡Genial! Tu solicitud para participar en \"Evento de Prueba\" ha sido aprobada. ¡Nos vemos en el evento!','SUCCESS','2025-10-11 23:06:47','2025-10-11 23:41:22',1),(10,11,'? Donación recibida','Has recibido una donación de fundacion-esperanza: 10kg de alimentos, 5 juguetes','SUCCESS','2025-10-11 23:06:47','2025-10-11 23:41:22',1),(11,11,'❌ Evento cancelado','El evento \"Evento de Prueba\" ha sido cancelado por la organización. Motivo: Condiciones climáticas adversas','ERROR','2025-10-11 23:06:47','2025-10-11 23:41:22',1),(12,11,'? Nueva solicitud de adhesión a evento','María González (organizacion-externa) quiere participar en \'orgCom\'. Ve a \'Gestión de Adhesiones\' para aprobar o rechazar la solicitud.','INFO','2025-10-11 23:52:24','2025-10-12 00:01:01',1),(13,13,'? Nueva solicitud de adhesión a evento','María González (organizacion-externa) quiere participar en \'orgCom\'. Ve a \'Gestión de Adhesiones\' para aprobar o rechazar la solicitud.','INFO','2025-10-11 23:52:24',NULL,0),(15,11,'? Nueva solicitud de adhesión a evento','María González (organizacion-externa) quiere participar en \'orgCom\'. Ve a \'Gestión de Adhesiones\' para aprobar o rechazar la solicitud.','INFO','2025-10-11 23:52:40','2025-10-11 23:56:25',1),(16,13,'? Nueva solicitud de adhesión a evento','María González (organizacion-externa) quiere participar en \'orgCom\'. Ve a \'Gestión de Adhesiones\' para aprobar o rechazar la solicitud.','INFO','2025-10-11 23:52:40',NULL,0),(17,11,'✅ Adhesión a evento aprobada','¡Genial! Tu solicitud para participar en \'orgCom\' ha sido aprobada. ¡Nos vemos en el evento!','SUCCESS','2025-10-11 23:52:40','2025-10-12 00:01:01',1),(18,11,'? Nueva solicitud de adhesión a evento','Juan Pérez (empuje-comunitario) quiere participar en \'Evento test-event-001\'. Ve a \'Gestión de Adhesiones\' para aprobar o rechazar la solicitud.','INFO','2025-10-12 00:21:27','2025-10-12 00:45:41',1),(19,13,'? Nueva solicitud de adhesión a evento','Juan Pérez (empuje-comunitario) quiere participar en \'Evento test-event-001\'. Ve a \'Gestión de Adhesiones\' para aprobar o rechazar la solicitud.','INFO','2025-10-12 00:21:27',NULL,0),(20,17,'Adhesión a evento aprobada','¡Genial! Tu solicitud para participar en \'test nuevo eventop\' ha sido aprobada. ¡Nos vemos en el evento!','SUCCESS','2025-10-12 01:02:45','2025-10-12 01:03:27',1),(21,17,'? ¡Donación recibida!','¡Excelente noticia esperanza_admin!\n\nLa organización \'empuje-comunitario\' ha respondido a tu solicitud de donaciones.\n\nDonaciones recibidas:\n• Arroz para comedor comunitario (8 kg)\\n• Abrigos para invierno (3 unidades)\n\nLas donaciones ya están disponibles en tu inventario. ¡Gracias por usar la red de colaboración!','SUCCESS','2025-10-12 03:27:34','2025-10-12 03:30:23',1),(22,11,'Adhesión a evento rechazada','Tu solicitud para participar en \'tEST2\' no fue aprobada.','WARNING','2025-10-12 15:08:39','2025-10-12 15:08:47',1),(23,26,'Adhesión a evento aprobada','¡Genial! Tu solicitud para participar en \'test eliminar\' ha sido aprobada. ¡Nos vemos en el evento!','SUCCESS','2025-10-12 19:36:41',NULL,0),(24,11,'Adhesión a evento aprobada','¡Genial! Tu solicitud para participar en \'test2\' ha sido aprobada. ¡Nos vemos en el evento!','SUCCESS','2025-10-12 19:40:28',NULL,0);
/*!40000 ALTER TABLE `notificaciones_usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ofertas_externas`
--

DROP TABLE IF EXISTS `ofertas_externas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ofertas_externas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `organizacion_donante` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `oferta_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `donaciones` json NOT NULL,
  `activa` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `organizacion_donante` (`organizacion_donante`,`oferta_id`),
  KEY `idx_ofertas_externas_activa` (`activa`),
  KEY `idx_ofertas_externas_organizacion` (`organizacion_donante`),
  KEY `idx_ofertas_externas_fecha` (`fecha_creacion`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ofertas_externas`
--

LOCK TABLES `ofertas_externas` WRITE;
/*!40000 ALTER TABLE `ofertas_externas` DISABLE KEYS */;
INSERT INTO `ofertas_externas` VALUES (1,'fundacion-esperanza','OFE-2025-001','[{\"cantidad\": \"20 latas\", \"categoria\": \"ALIMENTOS\", \"descripcion\": \"Conservas variadas\"}]',1,'2025-09-30 21:42:44','2025-09-30 21:42:44'),(2,'ong-solidaria','OFE-2025-002','[{\"cantidad\": \"15 prendas\", \"categoria\": \"ROPA\", \"descripcion\": \"Ropa de abrigo\"}, {\"cantidad\": \"8 unidades\", \"categoria\": \"JUGUETES\", \"descripcion\": \"Juegos de mesa\"}]',1,'2025-09-30 21:42:44','2025-09-30 21:42:44'),(3,'centro-comunitario','OFE-2025-003','[{\"cantidad\": \"25 kits\", \"categoria\": \"UTILES_ESCOLARES\", \"descripcion\": \"Kits escolares completos\"}]',1,'2025-09-30 21:42:44','2025-09-30 21:42:44'),(10,'empuje-comunitario','OFE-20251012-2a6c00f5','[{\"category\": \"ALIMENTOS\", \"quantity\": \"2\", \"description\": \"Muñecas de trapo\"}]',0,'2025-10-12 23:53:59','2025-10-13 00:04:52'),(11,'empuje-comunitario','OFE-20251012-342b8b46','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Alimentos no perecederos.\"}]',0,'2025-10-13 00:35:13','2025-10-13 00:36:20');
/*!40000 ALTER TABLE `ofertas_externas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `organizaciones`
--

DROP TABLE IF EXISTS `organizaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `organizaciones` (
  `id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre_completo` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `contacto_email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contacto_telefono` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `direccion` text COLLATE utf8mb4_unicode_ci,
  `activa` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `organizaciones`
--

LOCK TABLES `organizaciones` WRITE;
/*!40000 ALTER TABLE `organizaciones` DISABLE KEYS */;
INSERT INTO `organizaciones` VALUES ('centro-comunitario','Centro Comunitario Unidos','Centro de desarrollo comunitario','unidos@centro.org','+54-11-4567-8901','Mendoza, Argentina',1,'2025-09-30 23:54:01'),('empuje-comunitario','ONG Empuje Comunitario','Organización principal del sistema','admin@empuje.org','+54-11-1234-5678','Buenos Aires, Argentina',1,'2025-09-30 23:54:01'),('fundacion-esperanza','Fundación Esperanza','Fundación dedicada a la ayuda social','contacto@esperanza.org','+54-11-2345-6789','Córdoba, Argentina',1,'2025-09-30 23:54:01'),('ong-solidaria','ONG Solidaria','Organización de ayuda comunitaria','info@solidaria.org','+54-11-3456-7890','Rosario, Argentina',1,'2025-09-30 23:54:01');
/*!40000 ALTER TABLE `organizaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `participantes_evento`
--

DROP TABLE IF EXISTS `participantes_evento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `participantes_evento` (
  `evento_id` int NOT NULL,
  `usuario_id` int NOT NULL,
  `fecha_adhesion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`evento_id`,`usuario_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `participantes_evento_ibfk_1` FOREIGN KEY (`evento_id`) REFERENCES `eventos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `participantes_evento_ibfk_2` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `participantes_evento`
--

LOCK TABLES `participantes_evento` WRITE;
/*!40000 ALTER TABLE `participantes_evento` DISABLE KEYS */;
INSERT INTO `participantes_evento` VALUES (13,11,'2025-10-01 16:50:46'),(13,12,'2025-10-05 20:13:07'),(48,17,'2025-10-23 15:30:50'),(48,25,'2025-10-23 15:30:55'),(51,14,'2025-10-23 17:45:41'),(52,14,'2025-10-23 17:46:17'),(52,15,'2025-10-23 17:46:17'),(53,14,'2025-10-23 17:46:17'),(53,15,'2025-10-23 17:46:17'),(54,13,'2025-10-23 17:46:17'),(55,14,'2025-10-23 17:46:17'),(55,15,'2025-10-23 17:46:17'),(56,13,'2025-10-23 17:46:17'),(57,14,'2025-10-23 17:46:17'),(58,13,'2025-10-23 17:46:17');
/*!40000 ALTER TABLE `participantes_evento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `solicitudes_donaciones`
--

DROP TABLE IF EXISTS `solicitudes_donaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicitudes_donaciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `solicitud_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `donaciones` json NOT NULL,
  `estado` enum('ACTIVA','COMPLETADA','CANCELADA','DADA_DE_BAJA') COLLATE utf8mb4_unicode_ci DEFAULT 'ACTIVA',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `usuario_creacion` int DEFAULT NULL,
  `usuario_actualizacion` int DEFAULT NULL,
  `notas` text COLLATE utf8mb4_unicode_ci,
  `organization_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'empuje-comunitario',
  PRIMARY KEY (`id`),
  UNIQUE KEY `solicitud_id` (`solicitud_id`),
  KEY `usuario_creacion` (`usuario_creacion`),
  KEY `usuario_actualizacion` (`usuario_actualizacion`),
  KEY `idx_solicitudes_estado` (`estado`),
  KEY `idx_solicitudes_fecha` (`fecha_creacion`),
  KEY `idx_solicitudes_donaciones_estado` (`estado`),
  KEY `idx_solicitudes_donaciones_fecha` (`fecha_creacion`),
  KEY `idx_solicitudes_organization` (`organization_id`),
  CONSTRAINT `solicitudes_donaciones_ibfk_1` FOREIGN KEY (`usuario_creacion`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `solicitudes_donaciones_ibfk_2` FOREIGN KEY (`usuario_actualizacion`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `solicitudes_donaciones`
--

LOCK TABLES `solicitudes_donaciones` WRITE;
/*!40000 ALTER TABLE `solicitudes_donaciones` DISABLE KEYS */;
INSERT INTO `solicitudes_donaciones` VALUES (1,'REQ-2025-001','[{\"cantidad\": \"10 kg\", \"categoria\": \"ALIMENTOS\", \"descripcion\": \"Leche en polvo\"}]','DADA_DE_BAJA','2025-09-30 22:11:51','2025-10-11 17:45:20',NULL,NULL,'Urgente para programa de nutrición infantil','empuje-comunitario'),(2,'REQ-2025-002','[{\"cantidad\": \"50 prendas\", \"categoria\": \"ROPA\", \"descripcion\": \"Ropa de invierno\"}]','DADA_DE_BAJA','2025-09-30 22:11:51','2025-10-11 17:45:20',NULL,NULL,'Para familias en situación de vulnerabilidad','empuje-comunitario'),(3,'REQ-2025-003','[{\"cantidad\": \"Kit completo\", \"categoria\": \"MEDICAMENTOS\", \"descripcion\": \"Medicamentos básicos\"}]','DADA_DE_BAJA','2025-09-30 22:11:51','2025-10-11 17:45:20',NULL,NULL,'Para botiquín comunitario','empuje-comunitario'),(8,'REQ-1759271750823','[{\"category\": \"ALIMENTOS\", \"description\": \"5\"}]','DADA_DE_BAJA','2025-09-30 22:35:50','2025-10-11 17:45:20',NULL,NULL,'','empuje-comunitario'),(9,'REQ-1759274591463','[{\"category\": \"ROPA\", \"description\": \"ropa blanca\"}]','DADA_DE_BAJA','2025-09-30 23:23:11','2025-10-11 17:45:20',NULL,NULL,'','empuje-comunitario'),(13,'req-empuje-comunitario-test-1760205347','[{\"category\": \"ROPA\", \"description\": \"Ropa de invierno para niños\"}, {\"category\": \"ALIMENTOS\", \"description\": \"Alimentos no perecederos\"}]','DADA_DE_BAJA','2025-10-11 17:55:47','2025-10-11 18:06:40',11,NULL,'Solicitud de prueba','empuje-comunitario'),(14,'req-empuje-comunitario-test2-1760205347','[{\"category\": \"UTILES_ESCOLARES\", \"description\": \"Útiles escolares para primaria\"}, {\"category\": \"JUGUETES\", \"description\": \"Juguetes educativos\"}]','DADA_DE_BAJA','2025-10-11 17:55:47','2025-10-13 00:33:45',11,NULL,'Segunda solicitud de prueba','empuje-comunitario'),(15,'req-real-test-1760239654','[{\"cantidad\": \"10 kg\", \"urgencia\": \"MEDIA\", \"categoria\": \"Alimentos\", \"descripcion\": \"Arroz para comedor comunitario\"}, {\"cantidad\": \"5 unidades\", \"urgencia\": \"ALTA\", \"categoria\": \"Ropa\", \"descripcion\": \"Abrigos para invierno\"}]','ACTIVA','2025-10-12 03:27:34','2025-10-12 03:27:34',17,NULL,'Solicitud de prueba para test de notificaciones','fundacion-esperanza'),(16,'req-debug-1760239931','[{\"cantidad\": \"5 kg\", \"urgencia\": \"ALTA\", \"categoria\": \"Alimentos\", \"descripcion\": \"Leche en polvo\"}]','ACTIVA','2025-10-12 03:32:11','2025-10-12 03:32:11',17,NULL,'Solicitud para debug de Kafka','fundacion-esperanza');
/*!40000 ALTER TABLE `solicitudes_donaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `solicitudes_externas`
--

DROP TABLE IF EXISTS `solicitudes_externas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicitudes_externas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `organizacion_solicitante` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `solicitud_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `donaciones` json NOT NULL,
  `activa` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_solicitud` (`organizacion_solicitante`,`solicitud_id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `solicitudes_externas`
--

LOCK TABLES `solicitudes_externas` WRITE;
/*!40000 ALTER TABLE `solicitudes_externas` DISABLE KEYS */;
INSERT INTO `solicitudes_externas` VALUES (1,'empuje-comunitario','req-empuje-comunitario-aa4d2bd8','[{\"cantidad\": 50, \"categoria\": \"ALIMENTOS\", \"descripcion\": \"Arroz y fideos\"}, {\"cantidad\": 20, \"categoria\": \"ROPA\", \"descripcion\": \"Abrigos de invierno\"}]',1,'2025-10-06 02:17:43'),(2,'empuje-comunitario','req-empuje-comunitario-d34eea9d','[{\"category\": \"FOOD\", \"quantity\": 50, \"description\": \"Rice and pasta\"}]',1,'2025-10-06 02:17:43'),(3,'empuje-comunitario','req-empuje-comunitario-c73f7e92','[{\"category\": \"ROPA\", \"description\": \"ropa varias\"}]',1,'2025-10-11 17:41:54'),(6,'empuje-comunitario','req-empuje-comunitario-bc221c61','[{\"category\": \"ROPA\", \"description\": \"Ropa de prueba API\"}, {\"category\": \"ALIMENTOS\", \"description\": \"Alimentos de prueba API\"}]',1,'2025-10-11 17:55:12'),(7,'fundacion-esperanza','req-esperanza-1760205347','[{\"category\": \"ALIMENTOS\", \"description\": \"Comida para comedores comunitarios\"}, {\"category\": \"ROPA\", \"description\": \"Ropa para adultos mayores\"}]',0,'2025-10-11 17:55:47'),(8,'ong-solidaria','req-solidaria-1760205347','[{\"category\": \"JUGUETES\", \"description\": \"Juguetes para navidad\"}, {\"category\": \"UTILES_ESCOLARES\", \"description\": \"Mochilas y cuadernos\"}]',1,'2025-10-11 17:55:47'),(9,'empuje-comunitario','req-empuje-comunitario-8f00341b','[{\"category\": \"ROPA\", \"description\": \"Ropa de prueba API\"}, {\"category\": \"ALIMENTOS\", \"description\": \"Alimentos de prueba API\"}]',1,'2025-10-11 17:55:53'),(10,'empuje-comunitario','req-empuje-comunitario-3ad2d929','[{\"category\": \"ROPA\", \"description\": \"ropita\"}]',1,'2025-10-11 18:01:18'),(11,'empuje-comunitario','req-empuje-comunitario-f307dc28','[{\"category\": \"ROPA\", \"description\": \"Ropa de prueba API\"}, {\"category\": \"ALIMENTOS\", \"description\": \"Alimentos de prueba API\"}]',1,'2025-10-11 18:04:03'),(12,'empuje-comunitario','req-empuje-comunitario-2764f531','[{\"category\": \"ROPA\", \"description\": \"Ropa de empuje-comunitario\"}, {\"category\": \"ALIMENTOS\", \"description\": \"Alimentos de empuje-comunitario\"}]',1,'2025-10-11 18:04:34'),(13,'empuje-comunitario','req-empuje-comunitario-7a57d175','[{\"category\": \"ROPA\", \"description\": \"Ropa de fundacion-esperanza\"}, {\"category\": \"ALIMENTOS\", \"description\": \"Alimentos de fundacion-esperanza\"}]',1,'2025-10-11 18:04:34'),(14,'empuje-comunitario','req-empuje-comunitario-cf0c61c7','[{\"category\": \"ROPA\", \"description\": \"Ropa de empuje-comunitario\"}, {\"category\": \"ALIMENTOS\", \"description\": \"Alimentos de empuje-comunitario\"}]',1,'2025-10-11 18:05:00'),(15,'empuje-comunitario','req-empuje-comunitario-0fb72c86','[{\"category\": \"ROPA\", \"description\": \"Ropa de fundacion-esperanza\"}, {\"category\": \"ALIMENTOS\", \"description\": \"Alimentos de fundacion-esperanza\"}]',1,'2025-10-11 18:05:00'),(16,'empuje-comunitario','req-empuje-comunitario-52cc77fc','[{\"category\": \"ROPA\", \"description\": \"Ropa de empuje-comunitario\"}, {\"category\": \"ALIMENTOS\", \"description\": \"Alimentos de empuje-comunitario\"}]',1,'2025-10-11 18:05:15'),(17,'empuje-comunitario','req-empuje-comunitario-0a899b6c','[{\"category\": \"ROPA\", \"description\": \"Ropa de fundacion-esperanza\"}, {\"category\": \"ALIMENTOS\", \"description\": \"Alimentos de fundacion-esperanza\"}]',1,'2025-10-11 18:05:15'),(18,'empuje-comunitario','req-empuje-comunitario-f450dd3a','[{\"category\": \"ALIMENTOS\", \"description\": \"Alimentos para cancelar\"}]',1,'2025-10-11 18:07:05'),(19,'empuje-comunitario','req-empuje-comunitario-c340894e','[{\"category\": \"ROPA\", \"description\": \"ropatestser\"}]',1,'2025-10-11 18:09:36'),(20,'empuje-comunitario','req-empuje-comunitario-ac31bb23','[{\"category\": \"ROPA\", \"description\": \"Ropa de empuje-comunitario\"}, {\"category\": \"ALIMENTOS\", \"description\": \"Alimentos de empuje-comunitario\"}]',1,'2025-10-11 18:11:45'),(21,'empuje-comunitario','req-empuje-comunitario-74d9ddbe','[{\"category\": \"ROPA\", \"description\": \"Ropa de fundacion-esperanza\"}, {\"category\": \"ALIMENTOS\", \"description\": \"Alimentos de fundacion-esperanza\"}]',1,'2025-10-11 18:11:45'),(22,'empuje-comunitario','req-empuje-comunitario-db87b7bf','[{\"category\": \"ROPA\", \"description\": \"Prueba directa messaging-service\"}]',1,'2025-10-11 18:15:41'),(23,'empuje-comunitario','req-empuje-comunitario-04a8ca39','[{\"category\": \"ROPA\", \"description\": \"Prueba directa messaging-service\"}]',1,'2025-10-11 18:16:05'),(24,'empuje-comunitario','req-empuje-comunitario-545c43f7','[{\"category\": \"ALIMENTOS\", \"description\": \"Prueba sin organización\"}]',1,'2025-10-11 18:16:07'),(25,'empuje-comunitario','req-empuje-comunitario-33a70758','[{\"category\": \"ROPA\", \"description\": \"Prueba directa messaging-service\"}]',1,'2025-10-11 18:19:29'),(26,'empuje-comunitario','req-empuje-comunitario-ae50634b','[{\"category\": \"ALIMENTOS\", \"description\": \"Prueba sin organización\"}]',1,'2025-10-11 18:19:31'),(27,'empuje-comunitario','req-empuje-comunitario-0645517b','[{\"category\": \"ALIMENTOS\", \"description\": \"rarara\"}]',1,'2025-10-11 18:31:24'),(28,'fundacion-esperanza','req-fundacion-esperanza-ba352404','[{\"category\": \"ALIMENTOS\", \"description\": \"testester\"}]',0,'2025-10-11 18:31:45'),(29,'fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"description\": \"lo que haya\"}]',1,'2025-10-12 01:33:02'),(30,'esperanza-social','req-esperanza-social-8cf68dc4','[{\"cantidad\": 20, \"categoria\": \"ALIMENTOS\", \"descripcion\": \"Arroz integral 1kg\"}, {\"cantidad\": 15, \"categoria\": \"ROPA\", \"descripcion\": \"Camisetas talle L\"}]',1,'2025-10-12 17:35:29'),(31,'esperanza-social','req-esperanza-social-883ea55b','[{\"cantidad\": 20, \"categoria\": \"ALIMENTOS\", \"descripcion\": \"Arroz integral 1kg\"}, {\"cantidad\": 15, \"categoria\": \"ROPA\", \"descripcion\": \"Camisetas talle L\"}]',1,'2025-10-12 17:36:12'),(32,'esperanza-social','req-esperanza-social-b24b5592','[{\"cantidad\": 20, \"categoria\": \"ALIMENTOS\", \"descripcion\": \"Arroz integral 1kg\"}, {\"cantidad\": 15, \"categoria\": \"ROPA\", \"descripcion\": \"Camisetas talle L\"}]',1,'2025-10-12 17:53:10'),(33,'fundacion-esperanza','req-fundacion-esperanza-213032a4','[{\"category\": \"ROPA\", \"description\": \"1111\"}]',1,'2025-10-12 19:26:35'),(34,'empuje-comunitario','req-empuje-comunitario-c9849c20','[{\"category\": \"ALIMENTOS\", \"description\": \"Alimentos no perecederos varios.\"}]',1,'2025-10-13 00:31:53'),(35,'fundacion-esperanza','req-fundacion-esperanza-9fa332d2','[{\"category\": \"ROPA\", \"description\": \"ROPA TEST EXCEL\"}]',1,'2025-10-23 15:19:42'),(36,'fundacion-esperanza','req-fundacion-esperanza-7377a0e4','[{\"category\": \"ALIMENTOS\", \"description\": \"Fideos\"}]',1,'2025-10-23 16:29:09'),(37,'fundacion-esperanza','req-fundacion-esperanza-18a0a7fa','[{\"category\": \"ALIMENTOS\", \"description\": \"Alimentos no perecederos.\"}]',1,'2025-10-26 22:24:39');
/*!40000 ALTER TABLE `solicitudes_externas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `solicitudes_inscripcion`
--

DROP TABLE IF EXISTS `solicitudes_inscripcion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicitudes_inscripcion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `solicitud_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `apellido` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telefono` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `organizacion_destino` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `rol_solicitado` enum('COORDINADOR','VOLUNTARIO') COLLATE utf8mb4_unicode_ci NOT NULL,
  `mensaje` text COLLATE utf8mb4_unicode_ci,
  `estado` enum('PENDIENTE','APROBADA','DENEGADA') COLLATE utf8mb4_unicode_ci DEFAULT 'PENDIENTE',
  `fecha_solicitud` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_respuesta` timestamp NULL DEFAULT NULL,
  `usuario_revisor` int DEFAULT NULL,
  `comentarios_revisor` text COLLATE utf8mb4_unicode_ci,
  `datos_adicionales` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `solicitud_id` (`solicitud_id`),
  KEY `usuario_revisor` (`usuario_revisor`),
  KEY `idx_organizacion_estado` (`organizacion_destino`,`estado`),
  KEY `idx_fecha_solicitud` (`fecha_solicitud`),
  KEY `idx_estado` (`estado`),
  CONSTRAINT `solicitudes_inscripcion_ibfk_1` FOREIGN KEY (`usuario_revisor`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `solicitudes_inscripcion`
--

LOCK TABLES `solicitudes_inscripcion` WRITE;
/*!40000 ALTER TABLE `solicitudes_inscripcion` DISABLE KEYS */;
INSERT INTO `solicitudes_inscripcion` VALUES (1,'INS-2025-001','Roberto','García','roberto.garcia@email.com','+54911111111','empuje-comunitario','VOLUNTARIO','Me gustaría colaborar con la organización en actividades comunitarias','PENDIENTE','2025-10-06 01:28:21',NULL,NULL,NULL,NULL),(2,'INS-2025-002','Laura','Fernández','laura.fernandez@email.com','+54922222222','fundacion-esperanza','COORDINADOR','Tengo experiencia en gestión de proyectos sociales y me interesa coordinar actividades','PENDIENTE','2025-10-06 01:28:21',NULL,NULL,NULL,NULL),(3,'INS-2025-003','Miguel','Torres','miguel.torres@email.com','+54933333333','empuje-comunitario','VOLUNTARIO','Quiero ayudar en eventos y distribución de donaciones','PENDIENTE','2025-10-06 01:28:21',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `solicitudes_inscripcion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transferencias_donaciones`
--

DROP TABLE IF EXISTS `transferencias_donaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transferencias_donaciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tipo` enum('ENVIADA','RECIBIDA') COLLATE utf8mb4_unicode_ci NOT NULL,
  `organizacion_contraparte` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `solicitud_id` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `donaciones` json NOT NULL,
  `estado` enum('PENDIENTE','COMPLETADA','CANCELADA') COLLATE utf8mb4_unicode_ci DEFAULT 'COMPLETADA',
  `fecha_transferencia` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `usuario_registro` int DEFAULT NULL,
  `notas` text COLLATE utf8mb4_unicode_ci,
  `organizacion_propietaria` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_transferencias_tipo` (`tipo`),
  KEY `idx_transferencias_organizacion` (`organizacion_contraparte`),
  KEY `idx_transferencias_fecha` (`fecha_transferencia`),
  KEY `idx_transferencias_estado` (`estado`),
  KEY `idx_transferencias_organizacion_propietaria` (`organizacion_propietaria`,`fecha_transferencia` DESC),
  KEY `idx_transferencias_propietaria` (`organizacion_propietaria`)
) ENGINE=InnoDB AUTO_INCREMENT=82 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transferencias_donaciones`
--

LOCK TABLES `transferencias_donaciones` WRITE;
/*!40000 ALTER TABLE `transferencias_donaciones` DISABLE KEYS */;
INSERT INTO `transferencias_donaciones` VALUES (1,'ENVIADA','fundacion-esperanza','SOL-2024-001','[{\"category\": \"ALIMENTOS\", \"quantity\": \"10 latas\", \"description\": \"Puré de tomates\"}]','COMPLETADA','2025-09-30 21:42:44',1,'Transferencia completada exitosamente','empuje-comunitario'),(2,'RECIBIDA','ong-solidaria','SOL-2024-002','[{\"category\": \"JUGUETES\", \"quantity\": \"5 unidades\", \"description\": \"Pelotas de goma\"}]','COMPLETADA','2025-09-30 21:42:44',2,'Donación recibida en buen estado','ong-solidaria'),(3,'ENVIADA','centro-comunitario','SOL-2024-003','[{\"category\": \"UTILES_ESCOLARES\", \"quantity\": \"20 unidades\", \"description\": \"Cuadernos\"}]','COMPLETADA','2025-09-30 21:42:44',1,'Entrega coordinada para inicio de clases','empuje-comunitario'),(4,'ENVIADA','external-org','REQ-1759271750823','[{\"category\": \"ALIMENTOS\", \"quantity\": \"5\", \"description\": \"Arroz blanco 1kg\", \"inventoryId\": 3}]','COMPLETADA','2025-09-30 22:47:58',NULL,'','empuje-comunitario'),(5,'ENVIADA','external-org','REQ-1759274591463','[{\"category\": \"ROPA\", \"quantity\": \"5\", \"description\": \"Camisetas talle M\", \"inventoryId\": 4}]','COMPLETADA','2025-09-30 23:37:40',NULL,'','empuje-comunitario'),(6,'ENVIADA','empuje-comunitario','req-empuje-comunitario-0645517b','[{\"category\": \"ROPA\", \"quantity\": \"5\", \"description\": \"Ropa de invierno\", \"inventoryId\": 25, \"inventory_id\": 25, \"parsed_quantity\": 5}]','COMPLETADA','2025-10-11 18:53:56',NULL,'Transfer transfer-empuje-comunitario-b6bd20e4 by user 17','empuje-comunitario'),(7,'ENVIADA','empuje-comunitario','req-empuje-comunitario-0645517b','[{\"category\": \"JUGUETES\", \"quantity\": \"5\", \"description\": \"Juguetes navideños\", \"inventoryId\": 26, \"inventory_id\": 26, \"parsed_quantity\": 5}]','COMPLETADA','2025-10-11 19:04:07',NULL,'Transfer transfer-empuje-comunitario-10e82a14 by user 17','empuje-comunitario'),(8,'ENVIADA','empuje-comunitario','req-empuje-comunitario-0645517b','[{\"category\": \"JUGUETES\", \"quantity\": \"5\", \"description\": \"Juguetes navideños\", \"inventoryId\": 26, \"inventory_id\": 26, \"parsed_quantity\": 5}]','COMPLETADA','2025-10-11 19:09:49',NULL,'Transfer transfer-empuje-comunitario-cee3a987 by user 17','empuje-comunitario'),(9,'ENVIADA','empuje-comunitario','req-empuje-comunitario-0645517b','[{\"category\": \"JUGUETES\", \"quantity\": \"5\", \"description\": \"Juguetes navideños\", \"inventoryId\": 26, \"inventory_id\": 26, \"parsed_quantity\": 5}]','COMPLETADA','2025-10-11 19:16:28',NULL,'Transfer transfer-empuje-comunitario-30289744 by user 17','empuje-comunitario'),(10,'ENVIADA','empuje-comunitario','req-empuje-comunitario-0645517b','[{\"category\": \"JUGUETES\", \"quantity\": \"5\", \"description\": \"Juguetes navideños\", \"inventoryId\": 26, \"inventory_id\": 26, \"parsed_quantity\": 5}]','COMPLETADA','2025-10-11 19:46:24',NULL,'Transfer transfer-empuje-comunitario-b4dd2ef9 by user 17','empuje-comunitario'),(11,'ENVIADA','empuje-comunitario','req-empuje-comunitario-33a70758','[{\"category\": \"ROPA\", \"quantity\": \"5\", \"description\": \"Juguetes navideños\", \"inventoryId\": 26, \"inventory_id\": 26, \"parsed_quantity\": 5}]','COMPLETADA','2025-10-11 19:46:31',NULL,'Transfer transfer-empuje-comunitario-c650a3fa by user 17','empuje-comunitario'),(12,'ENVIADA','empuje-comunitario','req-empuje-comunitario-33a70758','[{\"category\": \"ROPA\", \"quantity\": \"5\", \"description\": \"Arroz para familias\", \"inventoryId\": 24, \"inventory_id\": 24, \"parsed_quantity\": 5}]','COMPLETADA','2025-10-11 19:46:49',NULL,'Transfer transfer-empuje-comunitario-03571140 by user 17','empuje-comunitario'),(13,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"quantity\": \"5\", \"description\": \"Muñecas de trapo\", \"inventoryId\": 7, \"inventory_id\": 7, \"parsed_quantity\": 5}]','COMPLETADA','2025-10-12 01:33:24',NULL,'Transfer transfer-empuje-comunitario-11ec4f46 by user 11','empuje-comunitario'),(14,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"sasa\", \"inventoryId\": 18, \"inventory_id\": 18, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 01:46:22',NULL,'Transfer transfer-empuje-comunitario-ba4ea7d6 by user 11','empuje-comunitario'),(15,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"sadasdasdasdas\", \"inventoryId\": 33, \"inventory_id\": 33, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 01:46:56',NULL,'Transfer transfer-empuje-comunitario-e4c671a3 by user 11','empuje-comunitario'),(16,'ENVIADA','empuje-comunitario','test-esperanza-001','[{\"category\": \"Alimentos\", \"quantity\": \"5L\", \"description\": \"Leche\"}]','COMPLETADA','2025-10-12 02:58:34',NULL,'Transferencia de prueba','fundacion-esperanza'),(17,'RECIBIDA','manos-solidarias','test-esperanza-002','[{\"category\": \"Ropa\", \"quantity\": \"10 pares\", \"description\": \"Zapatos\"}]','COMPLETADA','2025-10-12 02:58:34',NULL,'Transferencia de prueba','fundacion-esperanza'),(18,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"quantity\": \"3\", \"description\": \"TEST ESPERANZA DIRECT\", \"inventoryId\": 37, \"inventory_id\": 37, \"parsed_quantity\": 3}]','COMPLETADA','2025-10-12 03:21:19',NULL,'Transfer transfer-empuje-comunitario-63ef4871 by user 11','empuje-comunitario'),(19,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"TEST ESPERANZA DIRECT\", \"inventoryId\": 37, \"inventory_id\": 37, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 03:21:34',NULL,'Transfer transfer-empuje-comunitario-4b2f2247 by user 11','empuje-comunitario'),(20,'RECIBIDA','empuje-comunitario','req-real-test-1760239654','[{\"category\": \"Alimentos\", \"quantity\": \"8 kg\", \"description\": \"Arroz para comedor comunitario\"}, {\"category\": \"Ropa\", \"quantity\": \"3 unidades\", \"description\": \"Abrigos para invierno\"}]','COMPLETADA','2025-10-12 03:27:34',1,'Transferencia de prueba para test de notificaciones','fundacion-esperanza'),(21,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"esperanzazazaaaza\", \"inventoryId\": 35, \"inventory_id\": 35, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 03:30:43',NULL,'Transfer transfer-empuje-comunitario-ea91aa8b by user 11','empuje-comunitario'),(22,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"quantity\": \"5\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 15, \"inventory_id\": 15, \"parsed_quantity\": 5}]','COMPLETADA','2025-10-12 03:31:18',NULL,'Transfer transfer-empuje-comunitario-0d9fdb12 by user 11','empuje-comunitario'),(23,'ENVIADA','fundacion-esperanza','req-real-1760240020','[{\"quantity\": \"2\", \"inventoryId\": 37, \"inventory_id\": 37, \"parsed_quantity\": 2}]','COMPLETADA','2025-10-12 03:33:41',NULL,'Transfer transfer-empuje-comunitario-50f1e2f8 by user 11','empuje-comunitario'),(24,'ENVIADA','fundacion-esperanza','req-dynamic-1760240689','[{\"quantity\": \"1\", \"inventoryId\": 4, \"inventory_id\": 4, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 03:44:49',NULL,'Transfer transfer-empuje-comunitario-9c392149 by user 11','empuje-comunitario'),(25,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"quantity\": \"5\", \"description\": \"Lápices de colores\", \"inventoryId\": 9, \"inventory_id\": 9, \"parsed_quantity\": 5}]','COMPLETADA','2025-10-12 03:45:53',NULL,'Transfer transfer-empuje-comunitario-84c920d7 by user 11','empuje-comunitario'),(26,'ENVIADA','fundacion-esperanza','req-dynamic-1760240859','[{\"quantity\": \"1\", \"inventoryId\": 4, \"inventory_id\": 4, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 03:47:40',NULL,'Transfer transfer-empuje-comunitario-5d44e821 by user 11','empuje-comunitario'),(27,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Test donation simple\", \"inventoryId\": 19, \"inventory_id\": 19, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 03:58:53',NULL,'Transfer transfer-empuje-comunitario-8383e942 by user 11','empuje-comunitario'),(28,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 15, \"inventory_id\": 15, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 16:44:44',NULL,'Transfer transfer-empuje-comunitario-ed38da39 by user 11','empuje-comunitario'),(29,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 15, \"inventory_id\": 15, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 16:45:50',NULL,'Transfer transfer-empuje-comunitario-8a86f691 by user 11','empuje-comunitario'),(30,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"quantity\": \"5\", \"description\": \"esperanza\", \"inventoryId\": 31, \"inventory_id\": 31, \"parsed_quantity\": 5}]','COMPLETADA','2025-10-12 17:00:39',NULL,'Transfer transfer-empuje-comunitario-8886cc66 by user 11','empuje-comunitario'),(31,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"asdasd es\", \"inventoryId\": 32, \"inventory_id\": 32, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 17:01:02',NULL,'Transfer transfer-empuje-comunitario-78aca04d by user 11','empuje-comunitario'),(32,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"quantity\": \"111\", \"description\": \"eseseseses\", \"inventoryId\": 36, \"inventory_id\": 36, \"parsed_quantity\": 111}]','COMPLETADA','2025-10-12 17:01:38',NULL,'Transfer transfer-empuje-comunitario-a09c7015 by user 11','empuje-comunitario'),(33,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"sasa\", \"inventoryId\": 20, \"inventory_id\": 20, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 17:13:01',NULL,'Transfer transfer-empuje-comunitario-e5e3a8ba by user 11','empuje-comunitario'),(34,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-174658a9','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"sasa\", \"inventoryId\": 16, \"inventory_id\": 16, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 17:15:55',NULL,'Transfer transfer-empuje-comunitario-09441c69 by user 11','empuje-comunitario'),(35,'ENVIADA','esperanza-social','req-esperanza-social-883ea55b','[{\"category\": \"ROPA\", \"quantity\": \"5\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 12, \"inventory_id\": 12, \"parsed_quantity\": 5}, {\"category\": \"ROPA\", \"quantity\": \"8\", \"description\": \"Camisetas talle M\", \"inventoryId\": 4, \"inventory_id\": 4, \"parsed_quantity\": 8}]','COMPLETADA','2025-10-12 17:36:18',NULL,'Transfer transfer-empuje-comunitario-0190767a by user 11','empuje-comunitario'),(36,'ENVIADA','esperanza-social','direct-test-1760291686','[{\"category\": \"ALIMENTOS\", \"quantity\": \"3\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 12, \"inventory_id\": 12, \"parsed_quantity\": 3}]','COMPLETADA','2025-10-12 17:54:49',NULL,'Transfer transfer-empuje-comunitario-798e03a4 by user 11','empuje-comunitario'),(37,'RECIBIDA','empuje-comunitario','manual-test-request','[{\"category\": \"ALIMENTOS\", \"quantity\": \"5 unidades\", \"description\": \"Test manual transfer\"}]','COMPLETADA','2025-10-12 17:57:00',26,'Transferencia manual para testing','esperanza-social'),(38,'ENVIADA','esperanza-social','direct-test-1760292150','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 12, \"inventory_id\": 12, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:02:32',NULL,'Transfer transfer-empuje-comunitario-9a47c691 by user 11','empuje-comunitario'),(39,'ENVIADA','esperanza-social','simulated-request-001','[{\"category\": \"ALIMENTOS\", \"quantity\": \"10 kg\", \"description\": \"Arroz integral simulado\", \"inventoryId\": 12}]','COMPLETADA','2025-10-12 18:04:12',11,'Transferencia simulada completa','empuje-comunitario'),(40,'RECIBIDA','empuje-comunitario','simulated-request-001','[{\"category\": \"ALIMENTOS\", \"quantity\": \"10 kg\", \"description\": \"Arroz integral simulado\", \"inventoryId\": 12}]','COMPLETADA','2025-10-12 18:04:12',26,'Transferencia simulada recibida','esperanza-social'),(41,'ENVIADA','esperanza-social','req-esperanza-social-b24b5592','[{\"quantity\": \"1\", \"description\": \"Lápices de colores\", \"inventoryId\": 9, \"inventory_id\": 9, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:23:48',NULL,'Transfer transfer-empuje-comunitario-b7ef6df7 by user 11','empuje-comunitario'),(42,'ENVIADA','esperanza-social','real-test-1760293619','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 12, \"inventory_id\": 12, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:27:01',NULL,'Transfer transfer-empuje-comunitario-515f1d25 by user 11','empuje-comunitario'),(43,'ENVIADA','esperanza-social','real-test-1760293773','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 13, \"inventory_id\": 13, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:29:36',NULL,'Transfer transfer-empuje-comunitario-3c78ef09 by user 11','empuje-comunitario'),(44,'ENVIADA','esperanza-social','fix-request-1760293876','[{\"category\": \"ALIMENTOS\", \"quantity\": \"5 kg\", \"description\": \"Arroz blanco premium\", \"inventoryId\": 13}]','COMPLETADA','2025-10-12 18:31:17',11,'Transferencia fix completa','empuje-comunitario'),(45,'RECIBIDA','empuje-comunitario','fix-request-1760293876','[{\"category\": \"ALIMENTOS\", \"quantity\": \"5 kg\", \"description\": \"Arroz blanco premium\", \"inventoryId\": 13}]','COMPLETADA','2025-10-12 18:31:17',26,'Transferencia fix recibida','esperanza-social'),(46,'ENVIADA','esperanza-social','req-esperanza-social-b24b5592','[{\"quantity\": \"1\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 13, \"inventory_id\": 13, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:36:49',NULL,'Transfer transfer-empuje-comunitario-02bf7ea7 by user 11','empuje-comunitario'),(47,'ENVIADA','esperanza-social','real-test-1760294548','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 13, \"inventory_id\": 13, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:42:30',NULL,'Transfer transfer-empuje-comunitario-f2faac5d by user 11','empuje-comunitario'),(48,'ENVIADA','esperanza-social','real-test-1760294592','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 13, \"inventory_id\": 13, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:43:15',NULL,'Transfer transfer-empuje-comunitario-a9106027 by user 11','empuje-comunitario'),(49,'ENVIADA','esperanza-social','real-test-1760294648','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 13, \"inventory_id\": 13, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:44:11',NULL,'Transfer transfer-empuje-comunitario-f3fa35e4 by user 11','empuje-comunitario'),(50,'RECIBIDA','empuje-comunitario','real-test-1760294648','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 13, \"inventory_id\": 13, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:44:50',NULL,'Transferencia recibida automáticamente - procesada por consumer simulado','esperanza-social'),(51,'RECIBIDA','empuje-comunitario','real-test-1760294592','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 13, \"inventory_id\": 13, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:44:50',NULL,'Transferencia recibida automáticamente - procesada por consumer simulado','esperanza-social'),(52,'RECIBIDA','empuje-comunitario','real-test-1760294548','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 13, \"inventory_id\": 13, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:44:50',NULL,'Transferencia recibida automáticamente - procesada por consumer simulado','esperanza-social'),(53,'RECIBIDA','empuje-comunitario','req-esperanza-social-b24b5592','[{\"quantity\": \"1\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 13, \"inventory_id\": 13, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:44:50',NULL,'Transferencia recibida automáticamente - procesada por consumer simulado','esperanza-social'),(54,'RECIBIDA','empuje-comunitario','real-test-1760293773','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 13, \"inventory_id\": 13, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:44:50',NULL,'Transferencia recibida automáticamente - procesada por consumer simulado','esperanza-social'),(55,'RECIBIDA','empuje-comunitario','real-test-1760293619','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 12, \"inventory_id\": 12, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:44:50',NULL,'Transferencia recibida automáticamente - procesada por consumer simulado','esperanza-social'),(56,'RECIBIDA','empuje-comunitario','req-esperanza-social-b24b5592','[{\"quantity\": \"1\", \"description\": \"Lápices de colores\", \"inventoryId\": 9, \"inventory_id\": 9, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:44:50',NULL,'Transferencia recibida automáticamente - procesada por consumer simulado','esperanza-social'),(57,'RECIBIDA','empuje-comunitario','direct-test-1760292150','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 12, \"inventory_id\": 12, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:44:50',NULL,'Transferencia recibida automáticamente - procesada por consumer simulado','esperanza-social'),(58,'RECIBIDA','empuje-comunitario','direct-test-1760291686','[{\"category\": \"ALIMENTOS\", \"quantity\": \"3\", \"description\": \"Prueba de donación multi-org\", \"inventoryId\": 12, \"inventory_id\": 12, \"parsed_quantity\": 3}]','COMPLETADA','2025-10-12 18:44:50',NULL,'Transferencia recibida automáticamente - procesada por consumer simulado','esperanza-social'),(59,'ENVIADA','esperanza-social','req-esperanza-social-b24b5592','[{\"quantity\": \"1\", \"description\": \"asdasd esese\", \"inventoryId\": 34, \"inventory_id\": 34, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:50:29',NULL,'Transfer transfer-empuje-comunitario-54c7d29a by user 11','empuje-comunitario'),(60,'RECIBIDA','empuje-comunitario','req-esperanza-social-b24b5592','[{\"quantity\": \"1\", \"description\": \"asdasd esese\", \"inventoryId\": 34, \"inventory_id\": 34, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 18:50:29',NULL,'Transferencia recibida automáticamente - transfer-empuje-comunitario-54c7d29a','esperanza-social'),(61,'ENVIADA','esperanza-social','test-auto-1760295751','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Test automatización\", \"inventoryId\": 12, \"inventory_id\": 12, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 19:02:31',1,'Test para automatización','empuje-comunitario'),(62,'RECIBIDA','empuje-comunitario','test-auto-1760295751','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Test automatización\", \"inventoryId\": 12, \"inventory_id\": 12, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 19:02:31',NULL,'Transferencia recibida automáticamente - procesada por consumer automático','esperanza-social'),(63,'ENVIADA','esperanza-social','api-test-1760295817','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Test API directo\", \"inventoryId\": 12, \"inventory_id\": 12, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 19:03:37',11,'Test API directo','empuje-comunitario'),(64,'RECIBIDA','empuje-comunitario','api-test-1760295817','[{\"category\": \"ALIMENTOS\", \"quantity\": \"1\", \"description\": \"Test API directo\", \"inventoryId\": 12, \"inventory_id\": 12, \"parsed_quantity\": 1}]','COMPLETADA','2025-10-12 19:03:37',NULL,'Transferencia recibida automáticamente - procesada por consumer automático','esperanza-social'),(65,'ENVIADA','esperanza-social','complete-test-1760295862','[{\"category\": \"ROPA\", \"quantity\": \"3\", \"description\": \"Test automatización completa\", \"inventoryId\": 12, \"inventory_id\": 12, \"parsed_quantity\": 3}, {\"category\": \"ROPA\", \"quantity\": \"2\", \"description\": \"Camisetas para niños\", \"inventoryId\": 13, \"inventory_id\": 13, \"parsed_quantity\": 2}]','COMPLETADA','2025-10-12 19:04:22',11,'Test completo de automatización','empuje-comunitario'),(66,'RECIBIDA','empuje-comunitario','complete-test-1760295862','[{\"category\": \"ROPA\", \"quantity\": \"3\", \"description\": \"Test automatización completa\", \"inventoryId\": 12, \"inventory_id\": 12, \"parsed_quantity\": 3}, {\"category\": \"ROPA\", \"quantity\": \"2\", \"description\": \"Camisetas para niños\", \"inventoryId\": 13, \"inventory_id\": 13, \"parsed_quantity\": 2}]','COMPLETADA','2025-10-12 19:04:22',NULL,'Transferencia recibida automáticamente - procesada por consumer automático','esperanza-social'),(67,'ENVIADA','esperanza-social','req-esperanza-social-b24b5592','[{\"quantity\": \"5\", \"description\": \"Muñecas de trapo\", \"inventoryId\": 7}]','COMPLETADA','2025-10-12 19:24:25',11,'Transferencia directa','empuje-comunitario'),(68,'ENVIADA','esperanza-social','req-esperanza-social-b24b5592','[{\"quantity\": \"5\", \"description\": \"Test donation simple\", \"inventoryId\": 21}]','COMPLETADA','2025-10-12 19:25:15',11,'Transferencia directa','empuje-comunitario'),(69,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-213032a4','[{\"category\": \"ROPA\", \"quantity\": \"5\", \"description\": \"Lápices de colores\", \"inventoryId\": 9}]','COMPLETADA','2025-10-12 19:26:46',11,'Transferencia directa','empuje-comunitario'),(70,'RECIBIDA','empuje-comunitario','req-fundacion-esperanza-213032a4','[{\"category\": \"ROPA\", \"quantity\": \"5\", \"description\": \"Lápices de colores\", \"inventoryId\": 9}]','COMPLETADA','2025-10-12 19:26:46',NULL,'Transferencia recibida automáticamente - procesada por consumer automático','fundacion-esperanza'),(71,'ENVIADA','empuje-comunitario','req-empuje-comunitario-c9849c20','[{\"category\": \"ALIMENTOS\", \"quantity\": \"5\", \"description\": \"Arroz para familias\", \"inventoryId\": 24}]','COMPLETADA','2025-10-13 00:33:19',17,'Transferencia directa','fundacion-esperanza'),(72,'RECIBIDA','fundacion-esperanza','req-empuje-comunitario-c9849c20','[{\"category\": \"ALIMENTOS\", \"quantity\": \"5\", \"description\": \"Arroz para familias\", \"inventoryId\": 24}]','COMPLETADA','2025-10-13 00:33:19',NULL,'Transferencia recibida automáticamente - procesada por consumer automático','empuje-comunitario'),(73,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-213032a4','[{\"category\": \"ROPA\", \"quantity\": \"5\", \"description\": \"Prueba desde Node.js\", \"inventoryId\": 42}]','COMPLETADA','2025-10-23 00:44:28',11,'Transferencia directa','empuje-comunitario'),(74,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-9fa332d2','[{\"category\": \"ROPA\", \"quantity\": \"5\", \"description\": \"Prueba desde Node.js\", \"inventoryId\": 42}]','COMPLETADA','2025-10-23 15:19:57',11,'Transferencia directa','empuje-comunitario'),(75,'RECIBIDA','empuje-comunitario','req-fundacion-esperanza-9fa332d2','[{\"category\": \"ROPA\", \"quantity\": \"5\", \"description\": \"Prueba desde Node.js\", \"inventoryId\": 42}]','COMPLETADA','2025-10-23 15:19:57',NULL,'Transferencia recibida automáticamente - procesada por consumer automático','fundacion-esperanza'),(76,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-9fa332d2','[{\"category\": \"ROPA\", \"quantity\": \"2\", \"description\": \"Test donation simple\", \"inventoryId\": 22}]','COMPLETADA','2025-10-23 15:20:30',11,'Transferencia directa','empuje-comunitario'),(77,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-9fa332d2','[{\"category\": \"ROPA\", \"quantity\": \"15\", \"description\": \"TEST ESPERANZA DIRECT\", \"inventoryId\": 37}]','COMPLETADA','2025-10-23 15:20:53',11,'Transferencia directa','empuje-comunitario'),(78,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-9fa332d2','[{\"category\": \"ROPA\", \"quantity\": \"1\", \"description\": \"Pantalones infantiles\", \"inventoryId\": 5}]','COMPLETADA','2025-10-23 15:21:19',11,'Transferencia directa','empuje-comunitario'),(79,'ENVIADA','empuje-comunitario','req-empuje-comunitario-c9849c20','[{\"category\": \"JUGUETES\", \"quantity\": \"15\", \"description\": \"Juguetes navideños\", \"inventoryId\": 26}]','COMPLETADA','2025-10-23 15:40:51',17,'Transferencia directa','fundacion-esperanza'),(80,'ENVIADA','fundacion-esperanza','req-fundacion-esperanza-7377a0e4','[{\"category\": \"ALIMENTOS\", \"quantity\": \"78\", \"description\": \"TEST ESPERANZA DIRECT\", \"inventoryId\": 37}]','COMPLETADA','2025-10-23 16:29:24',11,'Transferencia directa','empuje-comunitario'),(81,'RECIBIDA','empuje-comunitario','req-fundacion-esperanza-7377a0e4','[{\"category\": \"ALIMENTOS\", \"quantity\": \"78\", \"description\": \"TEST ESPERANZA DIRECT\", \"inventoryId\": 37}]','COMPLETADA','2025-10-23 16:29:24',NULL,'Transferencia recibida automáticamente - procesada por consumer automático','fundacion-esperanza');
/*!40000 ALTER TABLE `transferencias_donaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre_usuario` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `apellido` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `telefono` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `rol` enum('PRESIDENTE','VOCAL','COORDINADOR','VOLUNTARIO') COLLATE utf8mb4_unicode_ci NOT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `organizacion` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'empuje-comunitario',
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre_usuario` (`nombre_usuario`),
  UNIQUE KEY `email` (`email`),
  KEY `idx_usuarios_nombre_usuario` (`nombre_usuario`),
  KEY `idx_usuarios_activo` (`activo`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'test_president','Test','President','+1234567890','test.president@example.com','test_hash','PRESIDENTE',0,'2025-10-26 21:08:17','2025-10-26 19:16:47','empuje-comunitario'),(2,'test_vocal','Test','Vocal','+1234567891','test.vocal@example.com','test_hash','VOCAL',0,'2025-10-26 21:08:17','2025-10-26 19:16:50','empuje-comunitario'),(11,'admin','Juan','Pérez','+54911234567','admin@empujecomunitario.org','$2b$12$OK.hgSSlmLLI7ogOF.7FW.r355fu4yP/lIGWp5vhzL7119clbdHOe','PRESIDENTE',1,'2025-09-30 14:17:10','2025-10-01 23:57:39','empuje-comunitario'),(12,'vocal1','María','González','+54911234568','maria@empujecomunitario.org','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','VOCAL',1,'2025-09-30 14:17:10','2025-10-01 02:25:43','empuje-comunitario'),(13,'coord1','Carlos','López','+54911234569','carlos@empujecomunitario.org','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','COORDINADOR',1,'2025-09-30 14:17:10','2025-10-01 02:25:43','empuje-comunitario'),(14,'vol1','AnaSAT','Martínez','+54911234570','ana@empujecomunitario.org','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','VOLUNTARIO',1,'2025-09-30 14:17:10','2025-10-01 02:25:43','empuje-comunitario'),(15,'vol2','Pedro','Rodríguez','+54911234571','pedro@empujecomunitario.org','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','VOLUNTARIO',1,'2025-09-30 14:17:10','2025-10-01 02:25:43','empuje-comunitario'),(16,'asd','asd','asd','','asd@test.com','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','VOLUNTARIO',0,'2025-09-30 15:02:11','2025-10-01 02:25:43','empuje-comunitario'),(17,'esperanza_admin','María','González','+54-11-1111-1111','maria@esperanza.org','$2b$12$gbY4laMDVSPmB2OJglzeKuGh2awEOhlp/y/6JpPAXIuJ84K.2wQFu','PRESIDENTE',1,'2025-10-01 00:13:15','2025-10-12 19:35:54','fundacion-esperanza'),(18,'esperanza_coord','Carlos','Ruiz','+54-11-2222-2222','carlos@esperanza.org','$2b$12$gbY4laMDVSPmB2OJglzeKuGh2awEOhlp/y/6JpPAXIuJ84K.2wQFu','COORDINADOR',1,'2025-10-01 00:13:15','2025-10-12 19:35:54','fundacion-esperanza'),(19,'solidaria_admin','Ana','López','+54-11-3333-3333','ana@solidaria.org','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','PRESIDENTE',1,'2025-10-01 00:13:15','2025-10-01 02:25:43','ong-solidaria'),(20,'solidaria_vol','Pedro','Martín','+54-11-4444-4444','pedro@solidaria.org','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','VOLUNTARIO',1,'2025-10-01 00:13:15','2025-10-01 02:25:43','ong-solidaria'),(21,'centro_admin','Laura','Fernández','+54-11-5555-5555','laura@centro.org','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','PRESIDENTE',1,'2025-10-01 00:13:15','2025-10-01 02:25:43','centro-comunitario'),(22,'centro_vocal','Diego','Silva','+54-11-6666-6666','diego@centro.org','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','VOCAL',1,'2025-10-01 00:13:15','2025-10-01 02:25:43','centro-comunitario'),(23,'test_user_debug','Test','User','123456789','test@debug.com','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','VOLUNTARIO',1,'2025-10-01 02:01:44','2025-10-01 02:25:43','fundacion-esperanza'),(24,'znicolasheredia@gmail.com','Ariel','Heredia','01137604650','irenevalleji25@gmail.com','8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918','VOLUNTARIO',1,'2025-10-01 02:02:56','2025-10-01 02:25:43','empuje-comunitario'),(25,'esperanza','esperanza','test','','test@asdasd.com','$2b$12$pEWkY2wQbqimruadlJoZLOe/WleG9ZVskotF1v9uDVhBGtwE99cHu','VOLUNTARIO',1,'2025-10-01 16:22:00','2025-10-01 16:22:00','fundacion-esperanza'),(26,'admin_esperanza','Laura','Fernández','+54911234572','admin@esperanza-social.org','$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS','PRESIDENTE',1,'2025-10-12 17:32:16','2025-10-12 17:32:16','esperanza-social'),(27,'coord_esperanza','Miguel','Torres','+54911234573','coord@esperanza-social.org','$2b$12$0H6FzOFCXKCUD0W6VKCq1ORcp995QBUUo6/ZuSTHY9V7fAIZ32zjS','COORDINADOR',1,'2025-10-12 17:32:16','2025-10-12 17:32:16','esperanza-social'),(28,'testuszz','testerrerer','test','','asd@testestt.com','$2b$12$dtfXolYLw/Yj.5Nh4q2ZieDYUsTEooCCn6pDlpskhiVXilkkyPm52','VOLUNTARIO',0,'2025-10-21 21:17:29','2025-10-26 19:16:43','empuje-comunitario');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-29 13:23:03
