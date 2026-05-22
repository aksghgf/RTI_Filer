-- ==========================================
-- STEP 1: CREATE THE USERS TABLE
-- ==========================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- STEP 2: CREATE THE RTI APPLICATIONS TABLE
-- ==========================================
CREATE TABLE rti_applications (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    raw_problem TEXT NOT NULL,
    detected_ministry VARCHAR(255) NOT NULL,
    final_draft TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);