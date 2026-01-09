-- ============================================
-- Supabase Migration Script
-- ============================================
-- This script will:
-- 1. Create the 'insiders' table
-- 2. Insert all your existing insider data
-- ============================================

-- Step 1: Create the table (run this first)
CREATE TABLE IF NOT EXISTS insiders (
    name TEXT PRIMARY KEY,
    wallet_address TEXT NOT NULL,
    webhook TEXT NOT NULL,
    min_dollar_amount NUMERIC DEFAULT 0,
    tag_everyone BOOLEAN DEFAULT false,
    min_price NUMERIC DEFAULT 0,
    max_price NUMERIC DEFAULT 1,
    -- Bio information (stored in Supabase, not local files)
    serial_id INTEGER,
    trading_style TEXT,
    hit_rate TEXT,
    main_markets TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 2: Create a function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Step 3: Create trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_insiders_updated_at ON insiders;
CREATE TRIGGER update_insiders_updated_at
    BEFORE UPDATE ON insiders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Step 4: Insert all your existing insiders
-- (This uses INSERT ... ON CONFLICT to avoid duplicates if you run it multiple times)

INSERT INTO insiders (name, wallet_address, webhook, min_price, max_price, tag_everyone, min_dollar_amount, serial_id)
VALUES
    ('Tyrone - DigitalPost (ALT)', '0x80cabdce3dd662f94d410e23152ee2fd66df2bf7', 'https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk', 0, 1, true, 100, 1),
    ('Tyrone - JubileeSun (ALT)', '0xc9762a84234edd08592cbba44bf8fd6943520ad5', 'https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk', 0, 1, false, 50, 2),
    ('Tyrone - PastaPizza (Main)', '0xec0bc5b9d6f9cf4e88706d1e3efe333c6ee669e6', 'https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk', 0, 1, true, 50, 3),
    ('Tyrone - Lovecountry (ALT)', '0xc18f1a8fc24eb3cfc424ffb2405348d532e9605a', 'https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk', 0, 1, false, 50, 4),
    ('Tyrone - 0XdAF (ALT)', '0xdaf51a2383f994537f851e5827fbab20d597661d', 'https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk', 0, 1, true, 100, 5),
    ('BAdiosB - Insider', '0x909fa9f89976058b8b3ab87adc502ec7415ea8c3', 'https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk', 0, 1, true, 10, 6),
    ('9TungSahur - Insider', '0x6c2c072a0aa8fb8b4faf9aecae5520541f3b2d2a', 'https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk', 0, 1, true, 0, 7),
    ('ricosuave666 - Insider', '0x0afc7ce56285bde1fbe3a75efaffdfc86d6530b2', 'https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk', 0, 1, true, 0, 8),
    ('PorcoRosso - Insider', '0xd5de5cad9ef22b16317fe30a4234c72ece3eac1a', 'https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk', 0, 1, true, 0, 9),
    ('KoolAid - Insider', '0x711cf2d57de4c9aa53dd2c0bff3a2bf818688495', 'https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk', 0, 1, true, 100, 10),
    ('Violet-Vinyl - Strike Markets Insider', '0x9eb1f9602242b2218f55275fbab16e7eb239fc21', 'https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk', 0, 1, true, 50, 11),
    ('Dumbeldor2003 - IDF Insider', '0x31646fb225a7743287e760e44923345644513033', 'https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk', 0, 1, true, 50, 12),
    ('Rico - AugsburgFClover', '0x509cd9d117e06a082df649a06e317195f048240a', 'https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk', 0, 1, true, 1, NULL),
    ('Rico - Alt (metushelah)', '0x4e74acf9447df43029fedc1fe592775110de6a9f', 'https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk', 0, 1, true, 1, NULL),
    ('Rico - Alt (ddinhouse)', '0x03727dd8df63b9aaedebb30db24a7f07522fa86b', 'https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk', 0, 1, true, 1, NULL),
    ('Rico - Alt (Roimeo5)', '0xe03e96656bb81d7079a3a84694b7a4a73bb7f375', 'https://discord.com/api/webhooks/1435978926416465951/sU9YdR8nFbJcNmKah9-wSAbbqsjv8Db-KeCDW-C_3KjqoplH_FLehYnB5RVZxObE79Nk', 0, 1, true, 1, NULL)
ON CONFLICT (name) 
DO UPDATE SET
    wallet_address = EXCLUDED.wallet_address,
    webhook = EXCLUDED.webhook,
    min_price = EXCLUDED.min_price,
    max_price = EXCLUDED.max_price,
    tag_everyone = EXCLUDED.tag_everyone,
    min_dollar_amount = EXCLUDED.min_dollar_amount,
    serial_id = COALESCE(EXCLUDED.serial_id, insiders.serial_id),
    updated_at = NOW();

-- Step 5: After running this SQL, run migrate_bio_to_supabase.py to migrate bio data from data.json
-- This will transfer trading_style, hit_rate, main_markets, and notes to Supabase

-- Step 5: Verify the data
SELECT name, wallet_address, min_dollar_amount, tag_everyone 
FROM insiders 
ORDER BY name;
