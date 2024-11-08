CREATE TABLE IF NOT EXISTS spacex_rockets (
    id SERIAL PRIMARY KEY,
    rocket_name VARCHAR(100) NOT NULL
);

INSERT INTO spacex_rockets (rocket_name) VALUES
('Falcon 1'),
('Falcon 9'),
('Falcon Heavy'),
('Starship')
ON CONFLICT DO NOTHING;