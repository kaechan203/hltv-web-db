CREATE DATABASE IF NOT EXISTS hltv;
USE hltv;
-- =====================================
-- 1) team 队伍表
-- =====================================
CREATE TABLE team (
    tid INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tname VARCHAR(100) NOT NULL UNIQUE,
    logo_url VARCHAR(255),
    point INT DEFAULT 0
);
-- =====================================
-- 2) player 选手表
-- =====================================
CREATE TABLE player (
    pid INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tid INT UNSIGNED NOT NULL, -- 所属队伍
    pname VARCHAR(100) NOT NULL,
    country VARCHAR(100),
    photo_url VARCHAR(255),
    player_rating DOUBLE,
    UNIQUE (pname, tid), -- 允许不同队伍选手同名
    FOREIGN KEY (tid) REFERENCES team(tid)
);
-- =====================================
-- 3) tournament 赛事表
-- =====================================
CREATE TABLE tournament (
    tournament_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tournament_name VARCHAR(100) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    team_num INT, -- 参赛队伍数量
    location VARCHAR(100),
    series VARCHAR(100),
    `type` VARCHAR(20),
    status INT DEFAULT 0 -- 0未开始 1进行中 2已结束
);
-- =====================================
-- 4) tournament_team 赛事-队伍关系表
-- =====================================
CREATE TABLE tournament_team (
    tid INT UNSIGNED NOT NULL,
    tournament_id INT UNSIGNED NOT NULL,
    status INT DEFAULT 0,
    placement VARCHAR(100),
    PRIMARY KEY (tid, tournament_id),
    FOREIGN KEY (tid) REFERENCES team(tid),
    FOREIGN KEY (tournament_id) REFERENCES tournament(tournament_id)
);
-- =====================================
-- 5) matches 单场比赛大局表
-- =====================================
CREATE TABLE `match` (
    match_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tournament_id INT UNSIGNED NOT NULL,
    tid1 INT UNSIGNED NOT NULL,
    tid2 INT UNSIGNED NOT NULL,
    team1_point INT DEFAULT 0,
    team2_point INT DEFAULT 0,
    winner_tid INT UNSIGNED,
    match_time DATETIME NOT NULL,
    bo_n INT,
    match_stage VARCHAR(50),
    status INT DEFAULT 0,
    FOREIGN KEY (tournament_id) REFERENCES tournament(tournament_id),
    FOREIGN KEY (tid1) REFERENCES team(tid),
    FOREIGN KEY (tid2) REFERENCES team(tid),
    FOREIGN KEY (winner_tid) REFERENCES team(tid)
);
-- =====================================
-- 6) match_stat 单场比赛小局表
-- =====================================
CREATE TABLE match_stat (
    stat_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    match_id INT UNSIGNED NOT NULL,
    map_name VARCHAR(50) NOT NULL,
    team1_round INT NOT NULL DEFAULT 0,
    team2_round INT NOT NULL DEFAULT 0,
    winning_tid INT UNSIGNED,
    FOREIGN KEY (match_id) REFERENCES `match`(match_id),
    FOREIGN KEY (winning_tid) REFERENCES team(tid)
);
-- =====================================
-- 7) player_match_stat 单场小局选手数据
-- =====================================
CREATE TABLE player_match_stat (
    player_match_stat_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    match_id INT UNSIGNED NOT NULL,
    stat_id INT UNSIGNED NOT NULL,
    pid INT UNSIGNED NOT NULL,
    kd DOUBLE,
    mks INT,
    kast INT,
    one_vs_x INT,
    `kill` INT,
    headshot INT,
    assist INT,
    death INT,
    adr DOUBLE,
    swing DOUBLE,
    rating DOUBLE,
    FOREIGN KEY (match_id) REFERENCES `match`(match_id),
    FOREIGN KEY (stat_id) REFERENCES match_stat(stat_id),
    FOREIGN KEY (pid) REFERENCES player(pid)
);
-- =====================================
-- DROP TABLE 顺序（从子表到父表）
-- =====================================
-- DROP TABLE IF EXISTS player_match_stat;
-- DROP TABLE IF EXISTS match_stat;
-- DROP TABLE IF EXISTS `match`;
-- DROP TABLE IF EXISTS tournament_team;
-- DROP TABLE IF EXISTS player;
-- DROP TABLE IF EXISTS team;
-- DROP TABLE IF EXISTS tournament;
-- =====================================
