"""
Async Database Manager with Schema Migrations for BSM.

This module provides:
- Async SQLite operations using aiosqlite
- Schema migration system
- Optional encryption for sensitive data
- Cloud sync preparation
- Full-text search capabilities
"""

import aiosqlite
import asyncio
import json
import hashlib
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import aiofiles

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class SourceType(Enum):
    """Types of content sources."""
    SELECTION = "selection"
    SCREENSHOT = "screenshot"
    FILE = "file"
    URL = "url"


@dataclass
class Analysis:
    """Data class for analysis records."""
    id: Optional[int] = None
    content_hash: str = ""
    original_text: str = ""
    source_type: SourceType = SourceType.SELECTION
    analysis_result: Dict[str, Any] = None
    attitude_mode: str = "balanced"
    llm_provider: str = ""
    confidence_score: float = 0.0
    tags: List[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    encrypted: bool = False
    
    def __post_init__(self):
        if self.analysis_result is None:
            self.analysis_result = {}
        if self.tags is None:
            self.tags = []


class Migration:
    """Base class for database migrations."""
    
    version: int = 0
    description: str = ""
    
    async def up(self, db: aiosqlite.Connection):
        """Apply the migration."""
        raise NotImplementedError
    
    async def down(self, db: aiosqlite.Connection):
        """Rollback the migration."""
        raise NotImplementedError


class Migration001_InitialSchema(Migration):
    """Initial database schema."""
    
    version = 1
    description = "Create initial tables"
    
    async def up(self, db: aiosqlite.Connection):
        """Create initial tables."""
        await db.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE NOT NULL,
                original_text TEXT NOT NULL,
                source_type TEXT NOT NULL,
                analysis_result TEXT NOT NULL,
                attitude_mode TEXT NOT NULL,
                llm_provider TEXT NOT NULL,
                confidence_score REAL,
                encrypted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (analysis_id) REFERENCES analyses (id) ON DELETE CASCADE,
                UNIQUE(analysis_id, tag)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                description TEXT,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        await db.execute('CREATE INDEX IF NOT EXISTS idx_content_hash ON analyses(content_hash)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON analyses(created_at)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_attitude_mode ON analyses(attitude_mode)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_tags ON tags(tag)')
    
    async def down(self, db: aiosqlite.Connection):
        """Drop all tables."""
        await db.execute('DROP TABLE IF EXISTS tags')
        await db.execute('DROP TABLE IF EXISTS analyses')
        await db.execute('DROP TABLE IF EXISTS schema_migrations')


class Migration002_FullTextSearch(Migration):
    """Add full-text search capabilities."""
    
    version = 2
    description = "Add FTS5 virtual table for full-text search"
    
    async def up(self, db: aiosqlite.Connection):
        """Create FTS5 virtual table."""
        await db.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS analyses_fts USING fts5(
                content_hash UNINDEXED,
                original_text,
                analysis_result,
                tags,
                content=analyses,
                content_rowid=id
            )
        ''')
        
        # Create triggers to keep FTS table in sync
        await db.execute('''
            CREATE TRIGGER IF NOT EXISTS analyses_ai AFTER INSERT ON analyses BEGIN
                INSERT INTO analyses_fts(rowid, content_hash, original_text, analysis_result)
                VALUES (new.id, new.content_hash, new.original_text, new.analysis_result);
            END
        ''')
        
        await db.execute('''
            CREATE TRIGGER IF NOT EXISTS analyses_ad AFTER DELETE ON analyses BEGIN
                DELETE FROM analyses_fts WHERE rowid = old.id;
            END
        ''')
        
        await db.execute('''
            CREATE TRIGGER IF NOT EXISTS analyses_au AFTER UPDATE ON analyses BEGIN
                UPDATE analyses_fts 
                SET original_text = new.original_text,
                    analysis_result = new.analysis_result
                WHERE rowid = new.id;
            END
        ''')
    
    async def down(self, db: aiosqlite.Connection):
        """Remove FTS table and triggers."""
        await db.execute('DROP TRIGGER IF EXISTS analyses_ai')
        await db.execute('DROP TRIGGER IF EXISTS analyses_ad')
        await db.execute('DROP TRIGGER IF EXISTS analyses_au')
        await db.execute('DROP TABLE IF EXISTS analyses_fts')


class Migration003_SyncSupport(Migration):
    """Add cloud sync support fields."""
    
    version = 3
    description = "Add sync metadata fields"
    
    async def up(self, db: aiosqlite.Connection):
        """Add sync-related columns."""
        await db.execute('ALTER TABLE analyses ADD COLUMN sync_id TEXT')
        await db.execute('ALTER TABLE analyses ADD COLUMN sync_version INTEGER DEFAULT 1')
        await db.execute('ALTER TABLE analyses ADD COLUMN sync_status TEXT DEFAULT "local"')
        await db.execute('ALTER TABLE analyses ADD COLUMN last_synced_at TIMESTAMP')
        
        await db.execute('CREATE INDEX IF NOT EXISTS idx_sync_id ON analyses(sync_id)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_sync_status ON analyses(sync_status)')
    
    async def down(self, db: aiosqlite.Connection):
        """SQLite doesn't support dropping columns, would need to recreate table."""
        pass


class AsyncDatabaseManager:
    """Async database manager with migration support."""
    
    MIGRATIONS = [
        Migration001_InitialSchema(),
        Migration002_FullTextSearch(),
        Migration003_SyncSupport(),
    ]
    
    def __init__(self, db_path: str, encryption_key: Optional[str] = None):
        self.db_path = db_path
        self.encryption_key = encryption_key
        self._fernet = Fernet(encryption_key.encode()) if encryption_key else None
        self._db: Optional[aiosqlite.Connection] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize database and run migrations."""
        if self._initialized:
            return
        
        # Ensure database directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Open database connection
        self._db = await aiosqlite.connect(self.db_path)
        
        # Enable foreign keys
        await self._db.execute("PRAGMA foreign_keys = ON")
        
        # Run migrations
        await self._run_migrations()
        
        self._initialized = True
        logger.info(f"Database initialized at {self.db_path}")
    
    async def close(self):
        """Close database connection."""
        if self._db:
            await self._db.close()
            self._db = None
            self._initialized = False
    
    async def _run_migrations(self):
        """Run pending database migrations."""
        # Create migrations table if needed
        await self._db.execute('''
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                description TEXT,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Get current version
        cursor = await self._db.execute(
            "SELECT MAX(version) FROM schema_migrations"
        )
        row = await cursor.fetchone()
        current_version = row[0] if row[0] else 0
        
        # Run pending migrations
        for migration in self.MIGRATIONS:
            if migration.version > current_version:
                logger.info(f"Running migration {migration.version}: {migration.description}")
                
                try:
                    await migration.up(self._db)
                    await self._db.execute(
                        "INSERT INTO schema_migrations (version, description) VALUES (?, ?)",
                        (migration.version, migration.description)
                    )
                    await self._db.commit()
                    logger.info(f"Migration {migration.version} completed")
                except Exception as e:
                    logger.error(f"Migration {migration.version} failed: {e}")
                    await self._db.rollback()
                    raise
    
    def _encrypt_text(self, text: str) -> str:
        """Encrypt text if encryption is enabled."""
        if self._fernet:
            return self._fernet.encrypt(text.encode()).decode()
        return text
    
    def _decrypt_text(self, text: str) -> str:
        """Decrypt text if encryption is enabled."""
        if self._fernet:
            try:
                return self._fernet.decrypt(text.encode()).decode()
            except Exception as e:
                logger.error(f"Decryption failed: {e}")
                return text
        return text
    
    def _generate_content_hash(self, text: str, attitude_mode: str) -> str:
        """Generate a hash for content and attitude mode."""
        content = f"{text}:{attitude_mode}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def save_analysis(self, analysis: Analysis) -> int:
        """Save an analysis to the database."""
        if not self._initialized:
            await self.initialize()
        
        # Generate content hash
        analysis.content_hash = self._generate_content_hash(
            analysis.original_text, 
            analysis.attitude_mode
        )
        
        # Prepare data
        original_text = self._encrypt_text(analysis.original_text) if analysis.encrypted else analysis.original_text
        analysis_result = json.dumps(analysis.analysis_result)
        
        try:
            # Check if analysis already exists
            cursor = await self._db.execute(
                "SELECT id FROM analyses WHERE content_hash = ?",
                (analysis.content_hash,)
            )
            existing = await cursor.fetchone()
            
            if existing:
                # Update existing
                analysis_id = existing[0]
                await self._db.execute('''
                    UPDATE analyses 
                    SET analysis_result = ?, confidence_score = ?, 
                        llm_provider = ?, updated_at = CURRENT_TIMESTAMP,
                        encrypted = ?
                    WHERE id = ?
                ''', (
                    analysis_result,
                    analysis.confidence_score,
                    analysis.llm_provider,
                    analysis.encrypted,
                    analysis_id
                ))
            else:
                # Insert new
                cursor = await self._db.execute('''
                    INSERT INTO analyses (
                        content_hash, original_text, source_type, 
                        analysis_result, attitude_mode, llm_provider, 
                        confidence_score, encrypted
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    analysis.content_hash,
                    original_text,
                    analysis.source_type.value,
                    analysis_result,
                    analysis.attitude_mode,
                    analysis.llm_provider,
                    analysis.confidence_score,
                    analysis.encrypted
                ))
                analysis_id = cursor.lastrowid
            
            # Update tags
            await self._update_tags(analysis_id, analysis.tags)
            
            await self._db.commit()
            return analysis_id
            
        except Exception as e:
            await self._db.rollback()
            logger.error(f"Failed to save analysis: {e}")
            raise
    
    async def _update_tags(self, analysis_id: int, tags: List[str]):
        """Update tags for an analysis."""
        # Delete existing tags
        await self._db.execute(
            "DELETE FROM tags WHERE analysis_id = ?",
            (analysis_id,)
        )
        
        # Insert new tags
        for tag in tags:
            await self._db.execute(
                "INSERT OR IGNORE INTO tags (analysis_id, tag) VALUES (?, ?)",
                (analysis_id, tag)
            )
    
    async def get_analysis(self, analysis_id: int) -> Optional[Analysis]:
        """Get an analysis by ID."""
        if not self._initialized:
            await self.initialize()
        
        cursor = await self._db.execute('''
            SELECT id, content_hash, original_text, source_type,
                   analysis_result, attitude_mode, llm_provider,
                   confidence_score, encrypted, created_at, updated_at
            FROM analyses WHERE id = ?
        ''', (analysis_id,))
        
        row = await cursor.fetchone()
        if not row:
            return None
        
        # Get tags
        tag_cursor = await self._db.execute(
            "SELECT tag FROM tags WHERE analysis_id = ?",
            (analysis_id,)
        )
        tags = [row[0] for row in await tag_cursor.fetchall()]
        
        # Decrypt if needed
        original_text = self._decrypt_text(row[2]) if row[8] else row[2]
        
        return Analysis(
            id=row[0],
            content_hash=row[1],
            original_text=original_text,
            source_type=SourceType(row[3]),
            analysis_result=json.loads(row[4]),
            attitude_mode=row[5],
            llm_provider=row[6],
            confidence_score=row[7],
            encrypted=row[8],
            created_at=datetime.fromisoformat(row[9]),
            updated_at=datetime.fromisoformat(row[10]),
            tags=tags
        )
    
    async def search_analyses(
        self,
        query: Optional[str] = None,
        attitude_mode: Optional[str] = None,
        provider: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0,
        use_fts: bool = True
    ) -> List[Analysis]:
        """Search analyses with various filters."""
        if not self._initialized:
            await self.initialize()
        
        analyses = []
        
        if query and use_fts:
            # Use full-text search
            sql = '''
                SELECT DISTINCT a.id, a.content_hash, a.original_text, a.source_type,
                       a.analysis_result, a.attitude_mode, a.llm_provider,
                       a.confidence_score, a.encrypted, a.created_at, a.updated_at
                FROM analyses a
                INNER JOIN analyses_fts fts ON a.id = fts.rowid
                WHERE analyses_fts MATCH ?
            '''
            params = [query]
        else:
            # Regular search
            sql = '''
                SELECT DISTINCT a.id, a.content_hash, a.original_text, a.source_type,
                       a.analysis_result, a.attitude_mode, a.llm_provider,
                       a.confidence_score, a.encrypted, a.created_at, a.updated_at
                FROM analyses a
                WHERE 1=1
            '''
            params = []
            
            if query:
                sql += " AND (a.original_text LIKE ? OR a.analysis_result LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])
        
        # Add filters
        if attitude_mode:
            sql += " AND a.attitude_mode = ?"
            params.append(attitude_mode)
        
        if provider:
            sql += " AND a.llm_provider = ?"
            params.append(provider)
        
        if tags:
            sql += f" AND EXISTS (SELECT 1 FROM tags t WHERE t.analysis_id = a.id AND t.tag IN ({','.join(['?']*len(tags))}))"
            params.extend(tags)
        
        # Add ordering and pagination
        sql += " ORDER BY a.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor = await self._db.execute(sql, params)
        rows = await cursor.fetchall()
        
        for row in rows:
            # Get tags for each analysis
            tag_cursor = await self._db.execute(
                "SELECT tag FROM tags WHERE analysis_id = ?",
                (row[0],)
            )
            tags = [r[0] for r in await tag_cursor.fetchall()]
            
            # Decrypt if needed
            original_text = self._decrypt_text(row[2]) if row[8] else row[2]
            
            analyses.append(Analysis(
                id=row[0],
                content_hash=row[1],
                original_text=original_text,
                source_type=SourceType(row[3]),
                analysis_result=json.loads(row[4]),
                attitude_mode=row[5],
                llm_provider=row[6],
                confidence_score=row[7],
                encrypted=row[8],
                created_at=datetime.fromisoformat(row[9]),
                updated_at=datetime.fromisoformat(row[10]),
                tags=tags
            ))
        
        return analyses
    
    async def delete_analysis(self, analysis_id: int) -> bool:
        """Delete an analysis."""
        if not self._initialized:
            await self.initialize()
        
        try:
            cursor = await self._db.execute(
                "DELETE FROM analyses WHERE id = ?",
                (analysis_id,)
            )
            await self._db.commit()
            return cursor.rowcount > 0
        except Exception as e:
            await self._db.rollback()
            logger.error(f"Failed to delete analysis: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        if not self._initialized:
            await self.initialize()
        
        stats = {}
        
        # Total analyses
        cursor = await self._db.execute("SELECT COUNT(*) FROM analyses")
        stats['total_analyses'] = (await cursor.fetchone())[0]
        
        # By attitude mode
        cursor = await self._db.execute('''
            SELECT attitude_mode, COUNT(*) 
            FROM analyses 
            GROUP BY attitude_mode
        ''')
        stats['by_attitude'] = dict(await cursor.fetchall())
        
        # By provider
        cursor = await self._db.execute('''
            SELECT llm_provider, COUNT(*) 
            FROM analyses 
            GROUP BY llm_provider
        ''')
        stats['by_provider'] = dict(await cursor.fetchall())
        
        # Popular tags
        cursor = await self._db.execute('''
            SELECT tag, COUNT(*) as count
            FROM tags
            GROUP BY tag
            ORDER BY count DESC
            LIMIT 10
        ''')
        stats['popular_tags'] = await cursor.fetchall()
        
        return stats
    
    async def export_data(self, output_path: str, encrypted: bool = False):
        """Export database to JSON file."""
        if not self._initialized:
            await self.initialize()
        
        analyses = await self.search_analyses(limit=10000)
        
        export_data = {
            'version': max(m.version for m in self.MIGRATIONS),
            'exported_at': datetime.now().isoformat(),
            'analyses': []
        }
        
        for analysis in analyses:
            data = asdict(analysis)
            # Convert datetime objects to strings
            data['created_at'] = data['created_at'].isoformat() if data['created_at'] else None
            data['updated_at'] = data['updated_at'].isoformat() if data['updated_at'] else None
            data['source_type'] = data['source_type'].value
            
            # Optionally encrypt sensitive data
            if encrypted and self._fernet:
                data['original_text'] = self._encrypt_text(data['original_text'])
                data['encrypted'] = True
            
            export_data['analyses'].append(data)
        
        async with aiofiles.open(output_path, 'w') as f:
            await f.write(json.dumps(export_data, indent=2))
        
        logger.info(f"Exported {len(analyses)} analyses to {output_path}")
    
    async def import_data(self, input_path: str):
        """Import data from JSON file."""
        if not self._initialized:
            await self.initialize()
        
        async with aiofiles.open(input_path, 'r') as f:
            content = await f.read()
            import_data = json.loads(content)
        
        imported_count = 0
        
        for data in import_data.get('analyses', []):
            # Convert string dates back to datetime
            if data.get('created_at'):
                data['created_at'] = datetime.fromisoformat(data['created_at'])
            if data.get('updated_at'):
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
            
            # Convert source_type string to enum
            data['source_type'] = SourceType(data['source_type'])
            
            # Create Analysis object
            analysis = Analysis(**data)
            
            try:
                await self.save_analysis(analysis)
                imported_count += 1
            except Exception as e:
                logger.error(f"Failed to import analysis: {e}")
        
        logger.info(f"Imported {imported_count} analyses from {input_path}")
