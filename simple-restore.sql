--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$216000$XTsgZUR6Cy5v$8tZ8JeWpO2luf6G+2hcuTFdleRUC+pqn53vCn3IrzRM=','2020-08-08 15:59:16.000000',1,'mmartin','Matthew','Martin','mr.matthew.f.martin@gmail.com',1,1,'2020-08-08 15:59:10.000000');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `homeauto_account`
--

LOCK TABLES `homeauto_account` WRITE;
/*!40000 ALTER TABLE `homeauto_account` DISABLE KEYS */;
INSERT INTO `homeauto_account` VALUES (1,'2020-08-08 16:00:50.837870','2020-08-08 16:00:50.837909','Decora',1,'mr.matthew.f.martin@gmail.com','QQKmER67n&!g5',''),(2,'2020-08-08 16:01:21.856360','2020-08-08 19:17:55.521949','Vivint',1,'mr.matthew.f.martin@gmail.com','!kIIFm$IM27tKPN2','');
/*!40000 ALTER TABLE `homeauto_account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `homeauto_bridge`
--

LOCK TABLES `homeauto_bridge` WRITE;
/*!40000 ALTER TABLE `homeauto_bridge` DISABLE KEYS */;
INSERT INTO `homeauto_bridge` VALUES (1,'2020-08-08 16:02:59.995429','2020-08-08 16:02:59.995467','Hue Bridge',1,'192.168.1.200','-Kmy6yYA7IDztgMBj7dxCDRQHBuo1eojPm3MfCUo',0,1);
/*!40000 ALTER TABLE `homeauto_bridge` ENABLE KEYS */;
UNLOCK TABLES;


--
-- Dumping data for table `homeauto_person`
--

LOCK TABLES `homeauto_person` WRITE;
/*!40000 ALTER TABLE `homeauto_person` DISABLE KEYS */;
INSERT INTO `homeauto_person` VALUES (1,0,1,'5712366182',1);
/*!40000 ALTER TABLE `homeauto_person` ENABLE KEYS */;
UNLOCK TABLES;

