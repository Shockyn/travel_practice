DROP SCHEMA IF EXISTS travel;
CREATE SCHEMA travel;
USE travel;

DROP TABLE IF EXISTS `geoinfos`;

CREATE TABLE `geoinfos` (
  `ID` CHAR(20) NOT NULL,
  `NAME` TEXT NOT NULL,
  `CITY` CHAR(20) NOT NULL,
  `ADDRESS` TEXT NOT NULL,
  `LNG` float NOT NULL,
  `LAT` float NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `ratings`;

CREATE TABLE `ratings` (
  `ID` CHAR(20) NOT NULL,
  `GG_REVIEWS` int NOT NULL,
  `GG_RATINGS` float NOT NULL,
  `TA_REVIEWS` int NOT NULL,
  `TA_RATINGS` float NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `types`;

CREATE TABLE `types` (
  `ID` CHAR(20) NOT NULL,
  `TYPES` TEXT NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `ID` CHAR(10) NOT NULL,
  `PLACE_ID` CHAR(20) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;