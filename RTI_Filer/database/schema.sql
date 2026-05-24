CREATE TABLE IF NOT EXISTS rti_applications (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    user_location VARCHAR(255) NOT NULL,
    problem_text TEXT NOT NULL,
    detected_ministry VARCHAR(255) NOT NULL,
    rti_draft TEXT NOT NULL,
    pdf_path VARCHAR(500),
    language VARCHAR(10) DEFAULT 'en',
    status VARCHAR(50) DEFAULT 'draft',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
