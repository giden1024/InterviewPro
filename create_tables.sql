-- Create Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(80) NOT NULL,
    avatar_url VARCHAR(255),
    is_active BOOLEAN DEFAULT 1,
    last_login_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create Resumes table
CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    file_path VARCHAR(255),
    file_type VARCHAR(50),
    file_size INTEGER,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create Interview Sessions table
CREATE TABLE IF NOT EXISTS interview_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    resume_id INTEGER,
    session_type VARCHAR(50) DEFAULT 'practice',
    status VARCHAR(50) DEFAULT 'active',
    total_questions INTEGER DEFAULT 0,
    answered_questions INTEGER DEFAULT 0,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    score FLOAT,
    feedback TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (resume_id) REFERENCES resumes (id)
);

-- Create Questions table
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category VARCHAR(100) NOT NULL,
    difficulty VARCHAR(50) DEFAULT 'medium',
    question_text TEXT NOT NULL,
    expected_answer TEXT,
    keywords TEXT,
    tags TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create Answers table
CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    session_id INTEGER,
    answer_text TEXT,
    audio_file_path VARCHAR(255),
    transcription TEXT,
    ai_feedback TEXT,
    score FLOAT,
    answer_type VARCHAR(50) DEFAULT 'text',
    time_taken INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (question_id) REFERENCES questions (id),
    FOREIGN KEY (session_id) REFERENCES interview_sessions (id)
);

-- Insert default user for testing
INSERT OR IGNORE INTO users (email, password_hash, username, is_active) 
VALUES ('393893095@qq.com', 'scrypt:32768:8:1$rGZyRoZMnf8ILcDj$6a8e5e0c8b8f8e4c8e4c8e4c8e4c8e4c8e4c8e4c8e4c8e4c8e4c8e4c8e4c8e4c8e4c8e4c8e4c8e4c8e4c8e4c8e4c8e4c8e4c8e4c', 'testuser', 1);

-- Insert some test questions
INSERT OR IGNORE INTO questions (category, difficulty, question_text, expected_answer, keywords) VALUES
('技术面试', 'medium', '请介绍一下你对JavaScript的理解', '应该包含JS基础概念、特性等', 'JavaScript,编程,前端'),
('行为面试', 'easy', '请介绍一下你自己', '应该包含个人背景、技能、经验等', '自我介绍,个人背景'),
('技术面试', 'hard', '解释一下什么是闭包，并给出一个实际应用的例子', '应该包含闭包的定义和实际应用', '闭包,JavaScript,作用域'),
('项目经验', 'medium', '描述一个你最有挑战性的项目', '应该包含项目背景、挑战、解决方案', '项目经验,挑战,解决方案'),
('技术面试', 'medium', '什么是RESTful API？它有哪些特点？', '应该包含REST原则和API设计', 'REST,API,Web服务'); 