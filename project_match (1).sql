-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主机： 127.0.0.1
-- 生成日期： 2025-05-05 09:31:32
-- 服务器版本： 10.4.32-MariaDB
-- PHP 版本： 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `project_match`
--

-- --------------------------------------------------------

--
-- 表的结构 `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 转存表中的数据 `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('490c03ecd47c');

-- --------------------------------------------------------

--
-- 表的结构 `groups`
--

CREATE TABLE `groups` (
  `id` int(11) NOT NULL,
  `group_name` varchar(100) NOT NULL,
  `member_ids` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`member_ids`)),
  `project_id` int(11) DEFAULT NULL,
  `supervisor_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- 表的结构 `projects`
--

CREATE TABLE `projects` (
  `id` int(11) NOT NULL,
  `title` varchar(100) DEFAULT NULL,
  `description` varchar(100) DEFAULT NULL,
  `research_field` varchar(100) DEFAULT NULL,
  `group_or_individual` varchar(100) DEFAULT NULL,
  `project_start_time` datetime DEFAULT NULL,
  `project_end_time` datetime DEFAULT NULL,
  `supervisor_id` int(11) DEFAULT NULL,
  `project_grade` varchar(10) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 转存表中的数据 `projects`
--

INSERT INTO `projects` (`id`, `title`, `description`, `research_field`, `group_or_individual`, `project_start_time`, `project_end_time`, `supervisor_id`, `project_grade`, `status`) VALUES
(2, 'AI Research Project2', 'Exploring transformer architectures', 'Artificial Intelligence', 'group', '2025-05-01 00:00:00', '2025-08-01 00:00:00', 1, '', 'Pending'),
(3, 'test', '123', 'ai', 'group', '2025-05-10 01:01:00', '2025-09-01 01:01:00', 3, '', 'Pending');

-- --------------------------------------------------------

--
-- 表的结构 `students`
--

CREATE TABLE `students` (
  `id` int(11) NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `user_group_identifier` varchar(20) DEFAULT NULL,
  `major` varchar(100) DEFAULT NULL,
  `faculty` varchar(100) DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 转存表中的数据 `students`
--

INSERT INTO `students` (`id`, `first_name`, `last_name`, `email`, `password`, `user_group_identifier`, `major`, `faculty`, `group_id`) VALUES
(3, 'alice', 'smith', 'alice.smith@student.uts.edu.au', '$2b$12$WIKlXaLoZaypbEUW.AeH8ODFg.eRbk8gkEli3QNcTVZuZoXRjvX0y', 'student', '', '', 0),
(5, 'yuxuan', 'wang', 'yuxuan.wang@student.uts.edu.au', '$2b$12$IoafUEUYJpnVRzhcIIwl1OTKb8HWOUInJaXYOoVovVyKRrcFnbO3y', 'student', NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- 表的结构 `student_groups`
--

CREATE TABLE `student_groups` (
  `id` int(11) NOT NULL,
  `group_name` varchar(100) DEFAULT NULL,
  `supervisor_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- 表的结构 `supervisors`
--

CREATE TABLE `supervisors` (
  `expertise` varchar(100) DEFAULT NULL,
  `faculty` varchar(100) DEFAULT NULL,
  `quota` int(11) DEFAULT NULL,
  `id` int(11) NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `user_group_identifier` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 转存表中的数据 `supervisors`
--

INSERT INTO `supervisors` (`expertise`, `faculty`, `quota`, `id`, `first_name`, `last_name`, `email`, `password`, `user_group_identifier`) VALUES
('Machine Learning', 'Engineering and IT', 3, 1, 'Alice', 'Smith', 'a.b@uts.edu.au', '$2b$12$kktqOspCFgHtsPVwDzAYguu4vQHX0Rde4UQW6xihfgHrC352jAVjq', 'supervisor'),
(NULL, NULL, NULL, 2, 'shixu', 'ding', 'shixu.ding@uts.edu.au', '$2b$12$BE8/Q42KFWn5IQan6xfzT.2fuEnPj/bXobb8/597OvB9Teh2wau6K', 'supervisor'),
(NULL, NULL, 3, 3, 'aa', 'bb', 'firstname.lastname@student.uts.edu.au', '$2b$12$KL/mzON8sFOnShknRBUjz.skwesJ5nj900PQPMfvdzK9FFlwp7ZXS', 'supervisor');

--
-- 转储表的索引
--

--
-- 表的索引 `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- 表的索引 `groups`
--
ALTER TABLE `groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `group_name` (`group_name`),
  ADD KEY `project_id` (`project_id`),
  ADD KEY `supervisor_id` (`supervisor_id`),
  ADD KEY `ix_groups_id` (`id`);

--
-- 表的索引 `projects`
--
ALTER TABLE `projects`
  ADD PRIMARY KEY (`id`),
  ADD KEY `supervisor_id` (`supervisor_id`),
  ADD KEY `ix_projects_id` (`id`);

--
-- 表的索引 `students`
--
ALTER TABLE `students`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_students_email` (`email`),
  ADD KEY `ix_students_id` (`id`);

--
-- 表的索引 `student_groups`
--
ALTER TABLE `student_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `group_name` (`group_name`),
  ADD KEY `supervisor_id` (`supervisor_id`),
  ADD KEY `ix_student_groups_id` (`id`);

--
-- 表的索引 `supervisors`
--
ALTER TABLE `supervisors`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `ix_supervisors_email` (`email`),
  ADD KEY `ix_supervisors_id` (`id`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `groups`
--
ALTER TABLE `groups`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用表AUTO_INCREMENT `projects`
--
ALTER TABLE `projects`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- 使用表AUTO_INCREMENT `students`
--
ALTER TABLE `students`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- 使用表AUTO_INCREMENT `student_groups`
--
ALTER TABLE `student_groups`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用表AUTO_INCREMENT `supervisors`
--
ALTER TABLE `supervisors`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- 限制导出的表
--

--
-- 限制表 `groups`
--
ALTER TABLE `groups`
  ADD CONSTRAINT `groups_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`),
  ADD CONSTRAINT `groups_ibfk_2` FOREIGN KEY (`supervisor_id`) REFERENCES `supervisors` (`id`);

--
-- 限制表 `projects`
--
ALTER TABLE `projects`
  ADD CONSTRAINT `projects_ibfk_1` FOREIGN KEY (`supervisor_id`) REFERENCES `supervisors` (`id`);

--
-- 限制表 `student_groups`
--
ALTER TABLE `student_groups`
  ADD CONSTRAINT `student_groups_ibfk_1` FOREIGN KEY (`supervisor_id`) REFERENCES `supervisors` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
