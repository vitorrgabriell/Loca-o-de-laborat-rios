CREATE DATABASE IF NOT EXISTS locacao_lab;
USE locacao_lab;

CREATE TABLE IF NOT EXISTS `laboratorios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `quantidade_computadores` int(11) NOT NULL,
  `hardware_computador` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `aplicacoes_laboratorios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome_aplicacao` varchar(100) NOT NULL,
  `versao` varchar(50) NOT NULL,
  `laboratorio_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `laboratorio_id` (`laboratorio_id`),
  CONSTRAINT `aplicacoes_laboratorios_ibfk_1` FOREIGN KEY (`laboratorio_id`) REFERENCES `laboratorios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `coordenadores` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `senha` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `disciplinas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `quantidade_alunos` int(11) NOT NULL,
  `professor` varchar(100) NOT NULL,
  `duracao` time NOT NULL,
  `horario_inicio` time NOT NULL,
  `horario_fim` time NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `professores` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `senha` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `requisitos_disciplina` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome_materia` varchar(100) NOT NULL,
  `requisito` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `responsavel_ti` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `senha` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `solicitacoes_aceitas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `laboratorio` varchar(255) DEFAULT NULL,
  `disciplina` varchar(255) DEFAULT NULL,
  `data` date DEFAULT NULL,
  `hora` time DEFAULT NULL,
  `saida` time DEFAULT NULL,
  `estado` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `solicitacoes_alocacao` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `laboratorio` varchar(100) NOT NULL,
  `data` date NOT NULL,
  `hora` time NOT NULL,
  `saida` time DEFAULT NULL,
  `estado` enum('Pendente','Aprovada','Rejeitada') NOT NULL,
  `disciplina` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `solicitacoes_recusadas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `laboratorio` varchar(255) DEFAULT NULL,
  `disciplina` varchar(255) DEFAULT NULL,
  `data` date DEFAULT NULL,
  `hora` time DEFAULT NULL,
  `saida` time DEFAULT NULL,
  `estado` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
