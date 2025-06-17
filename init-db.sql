-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS interview_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE interview_db;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(100),
    avatar_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
);

-- 创建简历表
CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INT NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
    parse_confidence FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_status (user_id, status),
    INDEX idx_created_at (created_at)
);

-- 创建简历解析结果表
CREATE TABLE IF NOT EXISTS resume_parse_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id INT NOT NULL,
    basic_info JSON,
    skills JSON,
    experience JSON,
    education JSON,
    projects JSON,
    raw_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
);

-- 创建面试表
CREATE TABLE IF NOT EXISTS interviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    resume_id INT NOT NULL,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    status ENUM('pending', 'active', 'paused', 'completed', 'cancelled') DEFAULT 'pending',
    interview_type VARCHAR(50) DEFAULT 'general',
    difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
    total_questions INT DEFAULT 0,
    current_question_index INT DEFAULT 0,
    started_at TIMESTAMP NULL,
    ended_at TIMESTAMP NULL,
    duration INT,
    overall_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_user_status (user_id, status)
);

-- 创建问题表
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id INT,
    question_text TEXT NOT NULL,
    question_type ENUM('technical', 'behavioral', 'situational') DEFAULT 'technical',
    difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
    category VARCHAR(100),
    expected_answer TEXT,
    scoring_criteria JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE,
    INDEX idx_resume_type (resume_id, question_type),
    INDEX idx_difficulty (difficulty)
);

-- 创建面试回答表
CREATE TABLE IF NOT EXISTS interview_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    question_id INT NOT NULL,
    answer_text TEXT,
    answer_audio_url VARCHAR(255),
    response_time INT,
    score FLOAT,
    feedback JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    INDEX idx_interview_question (interview_id, question_id)
);

-- 创建面试反馈表
CREATE TABLE IF NOT EXISTS interview_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    interview_id INT NOT NULL,
    overall_feedback TEXT,
    strengths JSON,
    weaknesses JSON,
    recommendations JSON,
    improvement_areas JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interview_id) REFERENCES interviews(id) ON DELETE CASCADE
);

-- 插入示例数据（可选）
INSERT IGNORE INTO users (email, password_hash, username) VALUES 
('demo@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uO9G', 'Demo User');

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_resumes_status ON resumes(status);
CREATE INDEX IF NOT EXISTS idx_interviews_status ON interviews(status);
CREATE INDEX IF NOT EXISTS idx_questions_type_difficulty ON questions(question_type, difficulty); 