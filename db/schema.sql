-- NURZING D1 schema (Cloudflare free tier: 5 GB, 5M reads/day, 100k writes/day)
CREATE TABLE IF NOT EXISTS bookings (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  reference      TEXT NOT NULL UNIQUE,
  care_type      TEXT NOT NULL,
  shift          TEXT NOT NULL,
  days           INTEGER NOT NULL DEFAULT 1,
  city           TEXT,
  area           TEXT,
  phone          TEXT NOT NULL,
  patient        TEXT,
  notes          TEXT,
  professional   TEXT,
  estimate_low   INTEGER,
  estimate_high  INTEGER,
  status         TEXT NOT NULL DEFAULT 'new',
  created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_bookings_created ON bookings(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_bookings_status  ON bookings(status);

CREATE TABLE IF NOT EXISTS applications (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  reference      TEXT NOT NULL UNIQUE,
  name           TEXT NOT NULL,
  phone          TEXT NOT NULL,
  designation    TEXT NOT NULL,
  qualification  TEXT,
  reg_type       TEXT,
  reg_number     TEXT,
  years          INTEGER DEFAULT 0,
  city           TEXT,
  area           TEXT,
  care_types     TEXT,
  notes          TEXT,
  status         TEXT NOT NULL DEFAULT 'new',
  created_at     TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_apps_created ON applications(created_at DESC);
