-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: localhost:8889
-- Generation Time: Apr 09, 2026 at 07:55 AM
-- Server version: 8.0.44
-- PHP Version: 8.3.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `conciergerie_desruelle`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id_user` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `avis`
--

CREATE TABLE `avis` (
  `id_avis` int NOT NULL,
  `date_avis` date NOT NULL,
  `message` text,
  `id_presta` int NOT NULL,
  `image` varchar(500) DEFAULT NULL,
  `video` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `categorie`
--

CREATE TABLE `categorie` (
  `id_categorie` int NOT NULL,
  `nom` varchar(100) NOT NULL,
  `description` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `categorie`
--

INSERT INTO `categorie` (`id_categorie`, `nom`, `description`) VALUES
(1, ' Entretien ', 'Vous avez régulièrement l’impression de vous laisser déborder par les tâches ménagères du quotidien et vous souhaitez en déléguer une partie à la Conciergerie Desruelle ? Vous désirez qu’une entreprise de nettoyage entretienne vos locaux professionnels dans la métropole lilloise ? En tant que syndic de copropriété, vous aimeriez confier l’entretien des espaces communs à une entreprise spécialisée ?\r\nL’objectif de notre conciergerie : vous faciliter la vie ! Pour cela, nous vous proposons un vaste éventail de prestations adaptées à vos besoins, réguliers comme ponctuels.\r\nNos spécialistes interviennent dans toute la métropole lilloise : Loos, Ronchin, Lomme, Villeneuve-d’Ascq… Nos services s’adressent à des clients particuliers, mais également aux entreprises de la région, aux collectivités et même aux syndics de copropriété. '),
(2, ' Multiservices ', ' Vous souhaitez remplacer la lampe de votre salon mais vous n’avez aucune connaissance en électricité ? Besoin d’une nouvelle table basse pour le salon et de conseils personnalisés pour la choisir ?\r\nNotre équipe de professionnels est en mesure de réaliser des travaux ou des réparations qui vous donneront entière satisfaction ');

-- --------------------------------------------------------

--
-- Table structure for table `client`
--

CREATE TABLE `client` (
  `id_user` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `disponibilite`
--

CREATE TABLE `disponibilite` (
  `id_user` int NOT NULL,
  `id_presta` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `media_avis`
--

CREATE TABLE `media_avis` (
  `id_media_avis` int NOT NULL,
  `media_avis` varchar(500) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `media_retour`
--

CREATE TABLE `media_retour` (
  `id_media_retour` int NOT NULL,
  `media_retour` varchar(500) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `notif`
--

CREATE TABLE `notif` (
  `id_notif` int NOT NULL,
  `message` text NOT NULL,
  `date_message` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `id_admin` int DEFAULT NULL,
  `id_prestation` int DEFAULT NULL,
  `a_lu` enum('Oui','Non') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `notif_tech`
--

CREATE TABLE `notif_tech` (
  `id_notif` int NOT NULL,
  `id_user` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `prestation`
--

CREATE TABLE `prestation` (
  `id_presta` int NOT NULL,
  `status` enum('en attente','confirmée','en cours','terminée') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `adresse` varchar(255) DEFAULT NULL,
  `complement_adresse` varchar(255) DEFAULT NULL,
  `prix_total` decimal(10,2) DEFAULT NULL,
  `nb_tech` int DEFAULT NULL,
  `debut_contrat` datetime DEFAULT NULL,
  `fin_contrat` datetime DEFAULT NULL,
  `id_user` int NOT NULL,
  `info_supp` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `relation_avis_media`
--

CREATE TABLE `relation_avis_media` (
  `id_media_avis` int NOT NULL,
  `id_avis` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `relation_retour_media`
--

CREATE TABLE `relation_retour_media` (
  `id_retour` int NOT NULL,
  `id_media_retour` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `relation_type_presta`
--

CREATE TABLE `relation_type_presta` (
  `id_presta` int NOT NULL,
  `id_type_presta` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `retour_presta`
--

CREATE TABLE `retour_presta` (
  `id_retour` int NOT NULL,
  `id_presta` int NOT NULL,
  `commentaire` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `technicien`
--

CREATE TABLE `technicien` (
  `id_user` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `type_presta`
--

CREATE TABLE `type_presta` (
  `id_type_presta` int NOT NULL,
  `nom` varchar(100) NOT NULL,
  `description` text,
  `prix` decimal(10,2) NOT NULL,
  `id_categorie` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `type_presta`
--

INSERT INTO `type_presta` (`id_type_presta`, `nom`, `description`, `prix`, `id_categorie`) VALUES
(1, 'Nettoyage après travaux', 'Votre chantier touche à sa fin mais la poussière et les résidus persistent ? Vous souhaitez emménager dans un espace sain sans l’ombre d’un gravat ? La Conciergerie Desruelle assure une remise au propre méticuleuse de vos locaux pour que vous n’ayez plus qu’à poser vos valises en toute sérénité.', 35.00, 1),
(2, 'Vitrerie', 'Traces de pluie, pollution ou empreintes ternissent vos fenêtres et baies vitrées ? Qu’il s’agisse de vitrines commerciales ou de surfaces domestiques, nos spécialistes garantissent une transparence impeccable et un maximum de lumière naturelle dans votre intérieur, sans aucune trace.', 45.00, 1),
(3, 'Ménage régulier', 'Vous rêvez de retrouver un intérieur impeccable chaque soir sans y consacrer vos week-ends ? Pour votre domicile ou vos bureaux, nous définissons un planning sur-mesure. Discrétion, ponctualité et rigueur sont les engagements de nos intervenants pour vous simplifier la vie au quotidien.', 28.50, 1),
(4, 'Entretien Extérieur', 'Mousses sur la terrasse ou allées encrassées par le temps ? L’aspect extérieur est la première image de votre propriété. Nos équipes assurent le nettoyage haute pression et l’entretien de vos espaces pour valoriser votre patrimoine et vous permettre de profiter de vos extérieurs dès les beaux jours.', 5.50, 1),
(5, 'Dépannage Plomberie', 'Un robinet capricieux qui fuit ou un joint à remplacer en urgence ? Pas besoin d’être un expert pour assurer le bon fonctionnement de votre installation. Notre équipe intervient rapidement pour vos petits dépannages, vous garantissant une tranquillité d’esprit et un confort retrouvé.', 65.00, 2),
(6, 'Petite Électricité', 'Une prise défectueuse, un luminaire à poser ou une envie de changer vos interrupteurs ? Nos professionnels sécurisent vos installations et réalisent vos petits travaux électriques avec soin, vous évitant ainsi toute manipulation risquée ou complexe.', 65.00, 2),
(7, 'Aide au Mobilier', 'Vous venez d’acheter de nouveaux meubles mais le montage vous semble interminable ? Vous souhaitez réagencer vos bureaux ? Nous nous occupons du montage et de l’installation. Gagnez du temps et évitez les efforts inutiles : tout sera parfaitement en place et prêt à l’emploi.', 40.00, 2),
(8, 'Peinture & Sols', 'Envie de rafraîchir vos murs ou de poser un nouveau parquet pour changer d’ambiance ? Qu’il s’agisse de peinture ou de pose de revêtement de sol, nous réalisons vos finitions avec une exigence artisanale pour transformer votre intérieur selon vos goûts et vos envies.', 0.00, 2);

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id_user` int NOT NULL,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `telephone` varchar(20) DEFAULT NULL,
  `adresse` varchar(255) DEFAULT NULL,
  `mdp` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id_user`);

--
-- Indexes for table `avis`
--
ALTER TABLE `avis`
  ADD PRIMARY KEY (`id_avis`),
  ADD KEY `id_presta` (`id_presta`);

--
-- Indexes for table `categorie`
--
ALTER TABLE `categorie`
  ADD PRIMARY KEY (`id_categorie`);

--
-- Indexes for table `client`
--
ALTER TABLE `client`
  ADD PRIMARY KEY (`id_user`);

--
-- Indexes for table `disponibilite`
--
ALTER TABLE `disponibilite`
  ADD PRIMARY KEY (`id_user`,`id_presta`),
  ADD KEY `id_presta` (`id_presta`);

--
-- Indexes for table `media_avis`
--
ALTER TABLE `media_avis`
  ADD PRIMARY KEY (`id_media_avis`);

--
-- Indexes for table `media_retour`
--
ALTER TABLE `media_retour`
  ADD PRIMARY KEY (`id_media_retour`);

--
-- Indexes for table `notif`
--
ALTER TABLE `notif`
  ADD PRIMARY KEY (`id_notif`),
  ADD KEY `id_admin` (`id_admin`),
  ADD KEY `id_prestation` (`id_prestation`);

--
-- Indexes for table `notif_tech`
--
ALTER TABLE `notif_tech`
  ADD PRIMARY KEY (`id_notif`,`id_user`),
  ADD KEY `id_user` (`id_user`);

--
-- Indexes for table `prestation`
--
ALTER TABLE `prestation`
  ADD PRIMARY KEY (`id_presta`),
  ADD KEY `id_user` (`id_user`);

--
-- Indexes for table `relation_avis_media`
--
ALTER TABLE `relation_avis_media`
  ADD PRIMARY KEY (`id_media_avis`,`id_avis`),
  ADD KEY `id_avis` (`id_avis`);

--
-- Indexes for table `relation_retour_media`
--
ALTER TABLE `relation_retour_media`
  ADD PRIMARY KEY (`id_retour`,`id_media_retour`),
  ADD KEY `id_media_retour` (`id_media_retour`);

--
-- Indexes for table `relation_type_presta`
--
ALTER TABLE `relation_type_presta`
  ADD PRIMARY KEY (`id_presta`,`id_type_presta`),
  ADD KEY `id_type_presta` (`id_type_presta`);

--
-- Indexes for table `retour_presta`
--
ALTER TABLE `retour_presta`
  ADD PRIMARY KEY (`id_retour`),
  ADD KEY `id_presta` (`id_presta`);

--
-- Indexes for table `technicien`
--
ALTER TABLE `technicien`
  ADD PRIMARY KEY (`id_user`);

--
-- Indexes for table `type_presta`
--
ALTER TABLE `type_presta`
  ADD PRIMARY KEY (`id_type_presta`),
  ADD KEY `id_categorie` (`id_categorie`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id_user`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `avis`
--
ALTER TABLE `avis`
  MODIFY `id_avis` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `categorie`
--
ALTER TABLE `categorie`
  MODIFY `id_categorie` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `media_avis`
--
ALTER TABLE `media_avis`
  MODIFY `id_media_avis` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `media_retour`
--
ALTER TABLE `media_retour`
  MODIFY `id_media_retour` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `notif`
--
ALTER TABLE `notif`
  MODIFY `id_notif` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `prestation`
--
ALTER TABLE `prestation`
  MODIFY `id_presta` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `retour_presta`
--
ALTER TABLE `retour_presta`
  MODIFY `id_retour` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `type_presta`
--
ALTER TABLE `type_presta`
  MODIFY `id_type_presta` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id_user` int NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `admin`
--
ALTER TABLE `admin`
  ADD CONSTRAINT `admin_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `user` (`id_user`) ON DELETE CASCADE;

--
-- Constraints for table `avis`
--
ALTER TABLE `avis`
  ADD CONSTRAINT `avis_ibfk_1` FOREIGN KEY (`id_presta`) REFERENCES `prestation` (`id_presta`) ON DELETE CASCADE;

--
-- Constraints for table `client`
--
ALTER TABLE `client`
  ADD CONSTRAINT `client_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `user` (`id_user`) ON DELETE CASCADE;

--
-- Constraints for table `disponibilite`
--
ALTER TABLE `disponibilite`
  ADD CONSTRAINT `disponibilite_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `technicien` (`id_user`) ON DELETE CASCADE,
  ADD CONSTRAINT `disponibilite_ibfk_2` FOREIGN KEY (`id_presta`) REFERENCES `prestation` (`id_presta`) ON DELETE CASCADE;

--
-- Constraints for table `notif`
--
ALTER TABLE `notif`
  ADD CONSTRAINT `notif_ibfk_1` FOREIGN KEY (`id_admin`) REFERENCES `admin` (`id_user`),
  ADD CONSTRAINT `notif_ibfk_2` FOREIGN KEY (`id_prestation`) REFERENCES `prestation` (`id_presta`);

--
-- Constraints for table `notif_tech`
--
ALTER TABLE `notif_tech`
  ADD CONSTRAINT `notif_tech_ibfk_1` FOREIGN KEY (`id_notif`) REFERENCES `notif` (`id_notif`) ON DELETE CASCADE,
  ADD CONSTRAINT `notif_tech_ibfk_2` FOREIGN KEY (`id_user`) REFERENCES `technicien` (`id_user`) ON DELETE CASCADE;

--
-- Constraints for table `prestation`
--
ALTER TABLE `prestation`
  ADD CONSTRAINT `prestation_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `client` (`id_user`);

--
-- Constraints for table `relation_avis_media`
--
ALTER TABLE `relation_avis_media`
  ADD CONSTRAINT `relation_avis_media_ibfk_1` FOREIGN KEY (`id_media_avis`) REFERENCES `media_avis` (`id_media_avis`) ON DELETE CASCADE,
  ADD CONSTRAINT `relation_avis_media_ibfk_2` FOREIGN KEY (`id_avis`) REFERENCES `avis` (`id_avis`) ON DELETE CASCADE;

--
-- Constraints for table `relation_retour_media`
--
ALTER TABLE `relation_retour_media`
  ADD CONSTRAINT `relation_retour_media_ibfk_1` FOREIGN KEY (`id_retour`) REFERENCES `retour_presta` (`id_retour`) ON DELETE CASCADE,
  ADD CONSTRAINT `relation_retour_media_ibfk_2` FOREIGN KEY (`id_media_retour`) REFERENCES `media_retour` (`id_media_retour`) ON DELETE CASCADE;

--
-- Constraints for table `relation_type_presta`
--
ALTER TABLE `relation_type_presta`
  ADD CONSTRAINT `relation_type_presta_ibfk_1` FOREIGN KEY (`id_presta`) REFERENCES `prestation` (`id_presta`) ON DELETE CASCADE,
  ADD CONSTRAINT `relation_type_presta_ibfk_2` FOREIGN KEY (`id_type_presta`) REFERENCES `type_presta` (`id_type_presta`);

--
-- Constraints for table `retour_presta`
--
ALTER TABLE `retour_presta`
  ADD CONSTRAINT `retour_presta_ibfk_1` FOREIGN KEY (`id_presta`) REFERENCES `prestation` (`id_presta`) ON DELETE CASCADE;

--
-- Constraints for table `technicien`
--
ALTER TABLE `technicien`
  ADD CONSTRAINT `technicien_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `user` (`id_user`) ON DELETE CASCADE;

--
-- Constraints for table `type_presta`
--
ALTER TABLE `type_presta`
  ADD CONSTRAINT `type_presta_ibfk_1` FOREIGN KEY (`id_categorie`) REFERENCES `categorie` (`id_categorie`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
ALTER TABLE `prestation` 
MODIFY COLUMN `status` ENUM('dans_panier', 'En attente', 'confirmée', 'en cours', 'terminée') NOT NULL;

CREATE TABLE absence_technicien (
  id_absence int NOT NULL AUTO_INCREMENT,
  id_user int NOT NULL,
  date_absence date NOT NULL,
  motif varchar(255) DEFAULT 'Congé',
  statut enum('En attente','Acceptée','Refusée') NOT NULL DEFAULT 'En attente',
  PRIMARY KEY (id_absence),
  KEY id_user (id_user),
  CONSTRAINT absence_technicien_ibfk_1 FOREIGN KEY (id_user) REFERENCES technicien (id_user) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;