-- --------------------------------------------------------
-- Servidor:                     192.168.0.5
-- Versão do servidor:           10.3.17-MariaDB-0+deb10u1 - Raspbian 10
-- OS do Servidor:               debian-linux-gnueabihf
-- HeidiSQL Versão:              10.2.0.5599
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;


-- Copiando estrutura do banco de dados para gardenberry
CREATE DATABASE IF NOT EXISTS `gardenberry` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `gardenberry`;

-- Copiando estrutura para tabela gardenberry.previsao
CREATE TABLE IF NOT EXISTS `previsao` (
  `datahora` datetime NOT NULL,
  `precipitacao` float NOT NULL,
  `temperatura` float NOT NULL,
  `fonte` int(11) NOT NULL,
  PRIMARY KEY (`datahora`,`fonte`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela gardenberry.regas
CREATE TABLE IF NOT EXISTS `regas` (
  `datahora` datetime NOT NULL,
  `tempo` float NOT NULL,
  PRIMARY KEY (`datahora`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- Exportação de dados foi desmarcado.

-- Copiando estrutura para tabela gardenberry.tempo
CREATE TABLE IF NOT EXISTS `tempo` (
  `datahora` datetime NOT NULL,
  `umidade` float NOT NULL,
  `temperatura` float NOT NULL,
  `precipitacao` float DEFAULT 0,
  `fonte` smallint(6) NOT NULL DEFAULT 0,
  PRIMARY KEY (`datahora`,`fonte`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- Exportação de dados foi desmarcado.

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
