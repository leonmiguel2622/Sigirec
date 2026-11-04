-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 03-11-2026 a las 16:43:55
-- Versión del servidor: 8.4.3
-- Versión de PHP: 8.3.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `sigirec_web`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `analisis_ia`
--

CREATE TABLE `analisis_ia` (
  `id_analisis` int UNSIGNED NOT NULL,
  `id_usuario` int UNSIGNED DEFAULT NULL,
  `id_botella` int UNSIGNED DEFAULT NULL,
  `imagen` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `botella_detectada` tinyint(1) DEFAULT '0',
  `tapa_detectada` tinyint(1) DEFAULT '0',
  `etiqueta_detectada` tinyint(1) DEFAULT '0',
  `confianza` decimal(5,2) DEFAULT NULL,
  `puntos_base` int UNSIGNED DEFAULT '0',
  `puntos_tapa` int UNSIGNED DEFAULT '0',
  `puntos_etiqueta` int UNSIGNED DEFAULT '0',
  `puntos_totales` int UNSIGNED DEFAULT '0',
  `estado_analisis` enum('PENDIENTE','PROCESANDO','IDENTIFICADO','NO_IDENTIFICADO','ERROR') COLLATE utf8mb4_general_ci DEFAULT 'PENDIENTE',
  `modelo_ia` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `version_modelo` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `fecha_analisis` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `analisis_ia`
--

INSERT INTO `analisis_ia` (`id_analisis`, `id_usuario`, `id_botella`, `imagen`, `botella_detectada`, `tapa_detectada`, `etiqueta_detectada`, `confianza`, `puntos_base`, `puntos_tapa`, `puntos_etiqueta`, `puntos_totales`, `estado_analisis`, `modelo_ia`, `version_modelo`, `fecha_analisis`) VALUES
(1, 10, NULL, NULL, 1, 0, 0, 34.02, 50, 0, 0, 50, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-15 19:35:15'),
(2, 10, NULL, NULL, 1, 0, 1, 90.30, 50, 0, 5, 55, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-15 19:35:33'),
(3, 10, NULL, NULL, 1, 0, 0, 90.74, 50, 0, 0, 50, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-15 19:35:50'),
(4, 10, NULL, NULL, 1, 1, 0, 92.49, 50, 10, 0, 60, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-15 19:36:10'),
(5, 10, NULL, NULL, 1, 1, 1, 93.79, 50, 10, 5, 65, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-15 19:36:39'),
(6, 10, NULL, NULL, 1, 0, 1, 87.80, 50, 0, 5, 55, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-15 19:54:08'),
(7, 10, NULL, NULL, 1, 0, 1, 78.65, 50, 0, 5, 55, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-15 19:54:18'),
(8, 10, NULL, NULL, 1, 0, 1, 90.09, 50, 0, 5, 55, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-16 21:59:31'),
(9, 10, NULL, NULL, 1, 0, 0, 10.31, 50, 0, 0, 50, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-17 22:29:40'),
(10, 10, NULL, NULL, 1, 0, 1, 73.73, 50, 0, 5, 55, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-17 22:30:49'),
(11, 10, NULL, NULL, 1, 0, 1, 72.96, 50, 0, 5, 55, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-17 22:31:21'),
(12, 10, NULL, NULL, 1, 0, 1, 42.93, 50, 0, 5, 55, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-18 06:13:45'),
(13, 10, NULL, NULL, 1, 1, 0, 34.69, 50, 10, 0, 60, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-18 06:13:59'),
(14, 10, NULL, NULL, 1, 0, 0, 13.11, 50, 0, 0, 50, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-18 07:28:51'),
(15, 10, NULL, NULL, 1, 1, 1, 83.99, 50, 10, 5, 65, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-18 11:30:19'),
(16, 10, NULL, NULL, 1, 0, 1, 17.14, 50, 0, 5, 55, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-18 11:31:04'),
(17, 10, NULL, NULL, 1, 1, 1, 77.39, 50, 10, 5, 65, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-18 11:34:28'),
(18, 10, NULL, NULL, 1, 1, 1, 93.78, 50, 10, 5, 65, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-18 23:09:34'),
(19, 10, NULL, NULL, 1, 1, 1, 92.16, 50, 10, 5, 65, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-18 23:11:01'),
(20, 10, NULL, NULL, 1, 1, 1, 95.08, 50, 10, 5, 65, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-18 23:14:16'),
(21, 10, NULL, NULL, 1, 1, 1, 91.68, 50, 10, 5, 65, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-18 23:14:25'),
(22, 10, NULL, NULL, 1, 1, 0, 91.44, 50, 10, 0, 60, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-18 23:15:36'),
(23, 10, NULL, NULL, 1, 1, 1, 73.60, 50, 10, 5, 65, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-19 06:36:42'),
(24, 10, NULL, NULL, 1, 1, 0, 55.56, 50, 10, 0, 60, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-19 06:52:45'),
(25, 10, NULL, NULL, 1, 0, 0, 20.10, 50, 0, 0, 50, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-19 07:41:27'),
(26, 10, NULL, NULL, 1, 1, 0, 63.59, 50, 10, 0, 60, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-19 08:18:04'),
(27, 10, NULL, NULL, 1, 0, 1, 76.11, 50, 0, 5, 55, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-19 08:18:59'),
(28, 10, NULL, NULL, 1, 1, 0, 55.32, 50, 10, 0, 60, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-19 11:18:25'),
(29, 10, NULL, NULL, 1, 0, 0, 63.85, 50, 0, 0, 50, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-19 11:28:18'),
(30, 10, NULL, NULL, 1, 0, 1, 81.08, 50, 0, 5, 55, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-08-19 11:36:37'),
(31, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:51:57'),
(32, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:08'),
(33, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:10'),
(34, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:11'),
(35, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:11'),
(36, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:11'),
(37, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:11'),
(38, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:11'),
(39, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:12'),
(40, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:12'),
(41, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:12'),
(42, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:12'),
(43, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:12'),
(44, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:12'),
(45, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:17'),
(46, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:18'),
(47, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:18'),
(48, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:18'),
(49, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 08:52:18'),
(50, 10, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-27 09:32:07'),
(51, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-28 07:04:25'),
(52, 11, NULL, NULL, 0, 0, 0, 24.46, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-28 07:04:57'),
(53, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-28 07:05:34'),
(54, 11, NULL, NULL, 0, 0, 0, 20.41, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-28 07:16:24'),
(55, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-28 07:16:49'),
(56, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-10-28 07:17:24'),
(57, 11, NULL, NULL, 0, 0, 0, 38.55, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:15:05'),
(58, 11, NULL, NULL, 0, 1, 0, 53.31, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:15:27'),
(59, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:15:41'),
(60, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:15:56'),
(61, 11, NULL, NULL, 0, 0, 0, 26.40, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:16:05'),
(62, 11, NULL, NULL, 0, 0, 0, 15.76, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:16:08'),
(63, 11, NULL, NULL, 1, 0, 0, 50.30, 50, 0, 0, 50, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:16:40'),
(64, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:17:18'),
(65, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:17:25'),
(66, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:17:27'),
(67, 11, NULL, NULL, 0, 0, 0, 21.53, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:17:28'),
(68, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:17:30'),
(69, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:17:31'),
(70, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:17:32'),
(71, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:17:33'),
(72, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:17:33'),
(73, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:17:34'),
(74, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:17:47'),
(75, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:17:48'),
(76, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:17:49'),
(77, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:17:50'),
(78, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:17:51'),
(79, 11, NULL, NULL, 0, 0, 0, 0.00, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:18:09'),
(80, 11, NULL, NULL, 0, 0, 0, 20.32, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:18:28'),
(81, 11, NULL, NULL, 1, 0, 0, 76.47, 50, 0, 0, 50, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:19:08'),
(82, 11, NULL, NULL, 0, 0, 0, 15.72, 0, 0, 0, 0, 'NO_IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:20:55'),
(83, 11, NULL, NULL, 1, 1, 0, 46.15, 50, 10, 0, 60, 'IDENTIFICADO', 'YOLO', 'train-5', '2026-11-03 11:21:08');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auditoria`
--

CREATE TABLE `auditoria` (
  `id_auditoria` int UNSIGNED NOT NULL,
  `id_usuario` int UNSIGNED DEFAULT NULL,
  `accion` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `tabla_afectada` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `id_registro` int UNSIGNED DEFAULT NULL,
  `descripcion` text COLLATE utf8mb4_general_ci,
  `ip` varchar(45) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `fecha` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `auditoria`
--

INSERT INTO `auditoria` (`id_auditoria`, `id_usuario`, `accion`, `tabla_afectada`, `id_registro`, `descripcion`, `ip`, `fecha`) VALUES
(1, 1, 'CANJE', 'productos', 1, 'Canje de 500 SIGIPUNTOS por \'Llaverito SIGIREC\' (Usuario ID: 3).', '127.0.0.1', '2026-08-19 11:10:03'),
(2, 1, 'CANJE', 'productos', 5, 'Canje de 1000 SIGIPUNTOS por \'Figura Decorativa SIGIREC\' (Usuario ID: 5).', '127.0.0.1', '2026-08-19 11:17:53'),
(3, 1, 'CANJE', 'productos', 3, 'Canje de 700 SIGIPUNTOS por \'Portal', '127.0.0.1', '2026-08-19 11:29:12'),
(4, 1, 'CANJE', 'productos', 3, 'Canje de 700 SIGIPUNTOS por \'Portal', '127.0.0.1', '2026-08-19 11:32:22'),
(5, 1, 'CANJE', 'productos', 3, 'Canje de 700 SIGIPUNTOS por \'Portal', '127.0.0.1', '2026-08-19 11:37:42'),
(6, 1, 'ACTUALIZAR', 'usuarios', 1, 'Se modificaron los datos del usuario Administrador SIGIREC (ID: 1). Contraseña actualizada.', '127.0.0.1', '2026-10-28 06:53:47');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `botellas`
--

CREATE TABLE `botellas` (
  `id_botella` int UNSIGNED NOT NULL,
  `nombre` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `tipo_material` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `puntos_base` int UNSIGNED DEFAULT '0',
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `canjes`
--

CREATE TABLE `canjes` (
  `id_canje` int UNSIGNED NOT NULL,
  `id_usuario` int UNSIGNED DEFAULT NULL,
  `id_producto` int UNSIGNED DEFAULT NULL,
  `total_puntos` int UNSIGNED DEFAULT '0',
  `fecha_canje` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `canjes`
--

INSERT INTO `canjes` (`id_canje`, `id_usuario`, `id_producto`, `total_puntos`, `fecha_canje`) VALUES
(1, 10, 1, 500, '2026-08-19 11:10:03'),
(2, 10, 5, 1000, '2026-08-19 11:17:53'),
(3, 10, 3, 700, '2026-08-19 11:29:12'),
(4, 10, 3, 700, '2026-08-19 11:32:22'),
(5, 10, 3, 700, '2026-08-19 11:37:42');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `comprobantes_reciclaje`
--

CREATE TABLE `comprobantes_reciclaje` (
  `id_comprobante` int UNSIGNED NOT NULL,
  `id_analisis` int UNSIGNED DEFAULT NULL,
  `id_usuario` int UNSIGNED DEFAULT NULL,
  `numero_comprobante` varchar(30) COLLATE utf8mb4_general_ci NOT NULL,
  `saldo_anterior` int UNSIGNED DEFAULT '0',
  `puntos_ganados` int UNSIGNED DEFAULT '0',
  `saldo_nuevo` int UNSIGNED DEFAULT '0',
  `fecha_comprobante` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `comprobantes_reciclaje`
--

INSERT INTO `comprobantes_reciclaje` (`id_comprobante`, `id_analisis`, `id_usuario`, `numero_comprobante`, `saldo_anterior`, `puntos_ganados`, `saldo_nuevo`, `fecha_comprobante`) VALUES
(1, 1, 10, 'SIGI-000001', 50, 50, 100, '2026-08-15 19:35:15'),
(2, 2, 10, 'SIGI-000002', 100, 55, 155, '2026-08-15 19:35:33'),
(3, 3, 10, 'SIGI-000003', 155, 50, 205, '2026-08-15 19:35:50'),
(4, 4, 10, 'SIGI-000004', 205, 60, 265, '2026-08-15 19:36:10'),
(5, 5, 10, 'SIGI-000005', 265, 65, 330, '2026-08-15 19:36:39'),
(6, 6, 10, 'SIGI-000006', 330, 55, 385, '2026-08-15 19:54:08'),
(7, 7, 10, 'SIGI-000007', 385, 55, 440, '2026-08-15 19:54:18'),
(8, 8, 10, 'SIGI-000008', 440, 55, 495, '2026-08-16 21:59:31'),
(9, 9, 10, 'SIGI-000009', 495, 50, 545, '2026-08-17 22:29:40'),
(10, 10, 10, 'SIGI-000010', 545, 55, 600, '2026-08-17 22:30:49'),
(11, 11, 10, 'SIGI-000011', 600, 55, 655, '2026-08-17 22:31:21'),
(12, 12, 10, 'SIGI-000012', 655, 55, 710, '2026-08-18 06:13:45'),
(13, 13, 10, 'SIGI-000013', 710, 60, 770, '2026-08-18 06:13:59'),
(14, 14, 10, 'SIGI-000014', 0, 50, 50, '2026-08-18 07:28:51'),
(15, 15, 10, 'SIGI-000015', 50, 65, 115, '2026-08-18 11:30:19'),
(16, 16, 10, 'SIGI-000016', 115, 55, 170, '2026-08-18 11:31:04'),
(17, 17, 10, 'SIGI-000017', 170, 65, 235, '2026-08-18 11:34:28'),
(18, 18, 10, 'SIGI-000018', 235, 65, 300, '2026-08-18 23:09:34'),
(19, 19, 10, 'SIGI-000019', 300, 65, 365, '2026-08-18 23:11:01'),
(20, 20, 10, 'SIGI-000020', 365, 65, 430, '2026-08-18 23:14:16'),
(21, 21, 10, 'SIGI-000021', 430, 65, 495, '2026-08-18 23:14:25'),
(22, 22, 10, 'SIGI-000022', 495, 60, 555, '2026-08-18 23:15:36'),
(23, 23, 10, 'SIGI-000023', 555, 65, 620, '2026-08-19 06:36:42'),
(24, 24, 10, 'SIGI-000024', 620, 60, 680, '2026-08-19 06:52:45'),
(25, 25, 10, 'SIGI-000025', 680, 50, 730, '2026-08-19 07:41:27'),
(26, 26, 10, 'SIGI-000026', 0, 60, 60, '2026-08-19 08:18:04'),
(27, 27, 10, 'SIGI-000027', 60, 55, 115, '2026-08-19 08:18:59'),
(28, 28, 10, 'SIGI-000028', 230, 60, 290, '2026-08-19 11:18:25'),
(29, 29, 10, 'SIGI-000029', 0, 50, 50, '2026-08-19 11:28:18'),
(30, 30, 10, 'SIGI-000030', 0, 55, 55, '2026-08-19 11:36:37'),
(31, 63, 11, 'SIGI-000063', 0, 50, 50, '2026-11-03 11:16:57');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `movimientos_puntos`
--

CREATE TABLE `movimientos_puntos` (
  `id_movimiento` int UNSIGNED NOT NULL,
  `id_usuario` int UNSIGNED DEFAULT NULL,
  `id_analisis` int UNSIGNED DEFAULT NULL,
  `id_canje` int UNSIGNED DEFAULT NULL,
  `tipo_movimiento` enum('RECICLAJE','CANJE','AJUSTE','BONIFICACION','PENALIZACION','REVERSION') COLLATE utf8mb4_general_ci NOT NULL,
  `puntos` int NOT NULL,
  `motivo` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `id_usuario_admin` int UNSIGNED DEFAULT NULL,
  `fecha_movimiento` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `movimientos_puntos`
--

INSERT INTO `movimientos_puntos` (`id_movimiento`, `id_usuario`, `id_analisis`, `id_canje`, `tipo_movimiento`, `puntos`, `motivo`, `id_usuario_admin`, `fecha_movimiento`) VALUES
(1, 10, NULL, NULL, 'BONIFICACION', 50, 'Prueba', 1, '2026-08-15 10:59:00'),
(2, 10, 1, NULL, 'RECICLAJE', 50, 'Reciclaje detectado por IA: botella', NULL, '2026-08-15 19:35:15'),
(3, 10, 2, NULL, 'RECICLAJE', 55, 'Reciclaje detectado por IA: botella + etiqueta', NULL, '2026-08-15 19:35:33'),
(4, 10, 3, NULL, 'RECICLAJE', 50, 'Reciclaje detectado por IA: botella', NULL, '2026-08-15 19:35:50'),
(5, 10, 4, NULL, 'RECICLAJE', 60, 'Reciclaje detectado por IA: botella + tapa', NULL, '2026-08-15 19:36:10'),
(6, 10, 5, NULL, 'RECICLAJE', 65, 'Reciclaje detectado por IA: botella + tapa + etiqueta', NULL, '2026-08-15 19:36:39'),
(7, 10, 6, NULL, 'RECICLAJE', 55, 'Reciclaje detectado por IA: botella + etiqueta', NULL, '2026-08-15 19:54:08'),
(8, 10, 7, NULL, 'RECICLAJE', 55, 'Reciclaje detectado por IA: botella + etiqueta', NULL, '2026-08-15 19:54:18'),
(9, 10, 8, NULL, 'RECICLAJE', 55, 'Reciclaje detectado por IA: botella + etiqueta', NULL, '2026-08-16 21:59:31'),
(10, 10, 9, NULL, 'RECICLAJE', 50, 'Reciclaje detectado por IA: botella', NULL, '2026-08-17 22:29:40'),
(11, 10, 10, NULL, 'RECICLAJE', 55, 'Reciclaje detectado por IA: botella + etiqueta', NULL, '2026-08-17 22:30:49'),
(12, 10, 11, NULL, 'RECICLAJE', 55, 'Reciclaje detectado por IA: botella + etiqueta', NULL, '2026-08-17 22:31:21'),
(13, 10, 12, NULL, 'RECICLAJE', 55, 'Reciclaje detectado por IA: botella + etiqueta', NULL, '2026-08-18 06:13:45'),
(14, 10, 13, NULL, 'RECICLAJE', 60, 'Reciclaje detectado por IA: botella + tapa', NULL, '2026-08-18 06:13:59'),
(15, 10, NULL, NULL, 'PENALIZACION', -770, 'intercambio de puntos', 1, '2026-08-18 07:14:56'),
(16, 10, 14, NULL, 'RECICLAJE', 50, 'Reciclaje detectado por IA: botella', NULL, '2026-08-18 07:28:51'),
(17, 10, 15, NULL, 'RECICLAJE', 65, 'Reciclaje detectado por IA: botella + tapa + etiqueta', NULL, '2026-08-18 11:30:19'),
(18, 10, 16, NULL, 'RECICLAJE', 55, 'Reciclaje detectado por IA: botella + etiqueta', NULL, '2026-08-18 11:31:04'),
(19, 10, 17, NULL, 'RECICLAJE', 65, 'Reciclaje detectado por IA: botella + tapa + etiqueta', NULL, '2026-08-18 11:34:28'),
(20, 10, 18, NULL, 'RECICLAJE', 65, 'Reciclaje detectado por IA: botella + tapa + etiqueta', NULL, '2026-08-18 23:09:34'),
(21, 10, 19, NULL, 'RECICLAJE', 65, 'Reciclaje detectado por IA: botella + tapa + etiqueta', NULL, '2026-08-18 23:11:01'),
(22, 10, 20, NULL, 'RECICLAJE', 65, 'Reciclaje detectado por IA: botella + tapa + etiqueta', NULL, '2026-08-18 23:14:16'),
(23, 10, 21, NULL, 'RECICLAJE', 65, 'Reciclaje detectado por IA: botella + tapa + etiqueta', NULL, '2026-08-18 23:14:25'),
(24, 10, 22, NULL, 'RECICLAJE', 60, 'Reciclaje detectado por IA: botella + tapa', NULL, '2026-08-18 23:15:36'),
(25, 10, 23, NULL, 'RECICLAJE', 65, 'Reciclaje detectado por IA: botella + tapa + etiqueta', NULL, '2026-08-19 06:36:42'),
(26, 10, 24, NULL, 'RECICLAJE', 60, 'Reciclaje detectado por IA: botella + tapa', NULL, '2026-08-19 06:52:45'),
(27, 10, 25, NULL, 'RECICLAJE', 50, 'Reciclaje detectado por IA: botella', NULL, '2026-08-19 07:41:27'),
(28, 10, 26, NULL, 'RECICLAJE', 60, 'Reciclaje detectado por IA: botella + tapa', NULL, '2026-08-19 08:18:04'),
(29, 10, 27, NULL, 'RECICLAJE', 55, 'Reciclaje detectado por IA: botella + etiqueta', NULL, '2026-08-19 08:18:59'),
(30, 10, NULL, 1, 'CANJE', -500, 'Canje de 500 SIGIPUNTOS por producto: Llaverito SIGIREC', 1, '2026-08-19 11:10:03'),
(31, 10, NULL, NULL, 'BONIFICACION', 5000, 'Prueba', 1, '2026-08-19 11:17:29'),
(32, 10, NULL, 2, 'CANJE', -1000, 'Canje de 1000 SIGIPUNTOS por producto: Figura Decorativa SIGIREC', 1, '2026-08-19 11:17:53'),
(33, 10, 28, NULL, 'RECICLAJE', 60, 'Reciclaje detectado por IA: botella + tapa', NULL, '2026-08-19 11:18:25'),
(34, 10, 29, NULL, 'RECICLAJE', 50, 'Reciclaje detectado por IA: botella', NULL, '2026-08-19 11:28:18'),
(35, 10, NULL, 3, 'CANJE', -700, 'Canje de 700 SIGIPUNTOS por producto: Portal', 1, '2026-08-19 11:29:12'),
(36, 10, NULL, 4, 'CANJE', -700, 'Canje de 700 SIGIPUNTOS por producto: Portal', 1, '2026-08-19 11:32:22'),
(37, 10, 30, NULL, 'RECICLAJE', 55, 'Reciclaje detectado por IA: botella + etiqueta', NULL, '2026-08-19 11:36:37'),
(38, 10, NULL, 5, 'CANJE', -700, 'Canje de 700 SIGIPUNTOS por producto: Portal', 1, '2026-08-19 11:37:42'),
(39, 11, 63, NULL, 'RECICLAJE', 50, 'Reciclaje detectado por IA: botella', NULL, '2026-11-03 11:16:57');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id_producto` int UNSIGNED NOT NULL,
  `nombre` varchar(150) COLLATE utf8mb4_general_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_general_ci,
  `imagen` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `costo_puntos` int UNSIGNED NOT NULL,
  `stock` int UNSIGNED DEFAULT '0',
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id_producto`, `nombre`, `descripcion`, `imagen`, `costo_puntos`, `stock`, `fecha_registro`) VALUES
(1, 'Llaverito SIGIREC', 'Llaverito impreso en 3D con dise', 'llavero-sigirec.png', 500, 9, '2026-08-14 21:10:40'),
(2, 'Mini Maceta Ecol', 'Mini maceta decorativa impresa en 3D para plantas peque', 'mini-maceta.png', 620, 8, '2026-08-14 21:10:40'),
(3, 'Portal', 'Portal', 'portalapices.png', 700, 3, '2026-08-14 21:10:40'),
(4, 'Organizador de Escritorio', 'Organizador de escritorio impreso en 3D para guardar ', 'organizador.png', 850, 5, '2026-08-14 21:10:40'),
(5, 'Figura Decorativa SIGIREC', 'Figura decorativa impresa en 3D con dise', 'figura-sigirec.png', 1000, 2, '2026-08-14 21:10:40');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int UNSIGNED NOT NULL,
  `numero_identificacion` varchar(30) COLLATE utf8mb4_general_ci NOT NULL,
  `clave_hash` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `nombre_completo` varchar(150) COLLATE utf8mb4_general_ci NOT NULL,
  `correo` varchar(150) COLLATE utf8mb4_general_ci NOT NULL,
  `telefono` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `tipo_usuario` enum('USUARIO','ADMINISTRADOR') COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'USUARIO',
  `rol` enum('APRENDIZ','INSTRUCTOR','AREA_ADMINISTRATIVA','EXTERNO') COLLATE utf8mb4_general_ci DEFAULT 'APRENDIZ',
  `programa_formacion` varchar(150) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `numero_ficha` varchar(30) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `puntos` int UNSIGNED NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id_usuario`, `numero_identificacion`, `clave_hash`, `nombre_completo`, `correo`, `telefono`, `tipo_usuario`, `rol`, `programa_formacion`, `numero_ficha`, `puntos`) VALUES
(1, '0000000000', 'scrypt:32768:8:1$PmseGkSIX9JAANmx$889c7568b911d71c23821ed3d2fccd252e03ac2a9a2d037a4c6cb56f59ab3ffc6addd58e2c1a97c82d6f443edf70a2211f4155634774091867ebbebc55406ffe', 'Administrador SIGIREC', 'admin@sigirec.invalid', 'None', 'ADMINISTRADOR', 'AREA_ADMINISTRATIVA', 'SIGIREC', '0000000', 0),
(10, '1101202260', 'scrypt:32768:8:1$3S6brIwaXjKJzo8V$b01b81423b2bb08012b14d06fd2bf5d5d796e2313d0acc7d9ac5be69854715461068eaa7d94d7b7f4d588c8f760f9d92247fdca650c01ddbef6d201bf09e7619', 'Camilo Hernandez', 'tigrecamilo09@gmail.com', '3166766519', 'USUARIO', 'AREA_ADMINISTRATIVA', 'Analisis y desarrollo de software', '3139687', 2410),
(11, '1095308502', 'scrypt:32768:8:1$CZWJ8zIJ1uV3Bddd$9215102645a85d0da99f66b2512002c6793d106106b3c7d654a4851bd49478c933a602aab03d8c90d8b6b8f730329c81a991e59d145b929dbf02e07cbc6fb5a9', 'Miguel Leon', 'leonjohan481@gmail.com', '3017011662', 'USUARIO', 'APRENDIZ', 'Analisis y desarrollo de software', '3139687', 50);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `analisis_ia`
--
ALTER TABLE `analisis_ia`
  ADD PRIMARY KEY (`id_analisis`),
  ADD KEY `fk_analisis_usuarios` (`id_usuario`),
  ADD KEY `fk_analisis_botellas` (`id_botella`),
  ADD KEY `idx_analisis_usuario_estado` (`id_usuario`,`estado_analisis`);

--
-- Indices de la tabla `auditoria`
--
ALTER TABLE `auditoria`
  ADD PRIMARY KEY (`id_auditoria`),
  ADD KEY `fk_auditoria_usuarios` (`id_usuario`);

--
-- Indices de la tabla `botellas`
--
ALTER TABLE `botellas`
  ADD PRIMARY KEY (`id_botella`);

--
-- Indices de la tabla `canjes`
--
ALTER TABLE `canjes`
  ADD PRIMARY KEY (`id_canje`),
  ADD KEY `fk_canjes_usuarios` (`id_usuario`),
  ADD KEY `idx_canjes_producto` (`id_producto`);

--
-- Indices de la tabla `comprobantes_reciclaje`
--
ALTER TABLE `comprobantes_reciclaje`
  ADD PRIMARY KEY (`id_comprobante`),
  ADD KEY `fk_comprobantes_analisis` (`id_analisis`),
  ADD KEY `fk_comprobantes_usuarios` (`id_usuario`);

--
-- Indices de la tabla `movimientos_puntos`
--
ALTER TABLE `movimientos_puntos`
  ADD PRIMARY KEY (`id_movimiento`),
  ADD KEY `fk_movimientos_usuarios` (`id_usuario`),
  ADD KEY `fk_movimientos_analisis` (`id_analisis`),
  ADD KEY `fk_movimientos_canjes` (`id_canje`),
  ADD KEY `fk_movimientos_admin` (`id_usuario_admin`),
  ADD KEY `idx_movimientos_analisis` (`id_analisis`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id_producto`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `id_usuario` (`id_usuario`),
  ADD UNIQUE KEY `numero_identificacion` (`numero_identificacion`),
  ADD UNIQUE KEY `correo` (`correo`),
  ADD UNIQUE KEY `telefono` (`telefono`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `analisis_ia`
--
ALTER TABLE `analisis_ia`
  MODIFY `id_analisis` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=84;

--
-- AUTO_INCREMENT de la tabla `auditoria`
--
ALTER TABLE `auditoria`
  MODIFY `id_auditoria` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `botellas`
--
ALTER TABLE `botellas`
  MODIFY `id_botella` int UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `canjes`
--
ALTER TABLE `canjes`
  MODIFY `id_canje` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `comprobantes_reciclaje`
--
ALTER TABLE `comprobantes_reciclaje`
  MODIFY `id_comprobante` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT de la tabla `movimientos_puntos`
--
ALTER TABLE `movimientos_puntos`
  MODIFY `id_movimiento` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=40;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id_producto` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `analisis_ia`
--
ALTER TABLE `analisis_ia`
  ADD CONSTRAINT `fk_analisis_botellas` FOREIGN KEY (`id_botella`) REFERENCES `botellas` (`id_botella`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_analisis_usuarios` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Filtros para la tabla `auditoria`
--
ALTER TABLE `auditoria`
  ADD CONSTRAINT `fk_auditoria_usuarios` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Filtros para la tabla `canjes`
--
ALTER TABLE `canjes`
  ADD CONSTRAINT `fk_canjes_usuarios` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Filtros para la tabla `comprobantes_reciclaje`
--
ALTER TABLE `comprobantes_reciclaje`
  ADD CONSTRAINT `fk_comprobantes_analisis` FOREIGN KEY (`id_analisis`) REFERENCES `analisis_ia` (`id_analisis`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_comprobantes_usuarios` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Filtros para la tabla `movimientos_puntos`
--
ALTER TABLE `movimientos_puntos`
  ADD CONSTRAINT `fk_movimientos_admin` FOREIGN KEY (`id_usuario_admin`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_movimientos_analisis` FOREIGN KEY (`id_analisis`) REFERENCES `analisis_ia` (`id_analisis`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_movimientos_canjes` FOREIGN KEY (`id_canje`) REFERENCES `canjes` (`id_canje`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_movimientos_usuarios` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
