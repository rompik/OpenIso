-- Symbol sources: companies, projects, standards that define SKEY symbols
-- source_type: 'standard' | 'company' | 'project'
CREATE TABLE IF NOT EXISTS symbol_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'standard',
    version TEXT,
    description TEXT,
    url TEXT,
    CHECK (source_type IN ('standard', 'company', 'project'))
);

-- Default source: ISOGEN standard by Alias Limited
INSERT OR IGNORE INTO symbol_sources (id, name, source_type, version, description, url)
VALUES (1, 'ISOGEN / Alias Limited', 'standard', '2008',
        'ISOGEN Symbol Key (SKEY) Definitions, Copyright 1991-2008 Alias Limited',
        'http://www.alias.ltd.uk');
