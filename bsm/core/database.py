import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib

class DatabaseManager:
    """Manages SQLite database for storing BSM analysis history."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_hash TEXT UNIQUE NOT NULL,
                    original_text TEXT NOT NULL,
                    source_type TEXT NOT NULL,  -- 'selection', 'screenshot'
                    analysis_result TEXT NOT NULL,  -- JSON string
                    attitude_mode TEXT NOT NULL,
                    llm_provider TEXT NOT NULL,
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    FOREIGN KEY (analysis_id) REFERENCES analyses (id) ON DELETE CASCADE
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_content_hash ON analyses(content_hash)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at ON analyses(created_at)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_attitude_mode ON analyses(attitude_mode)
            ''')
    
    def _generate_content_hash(self, text: str, attitude_mode: str) -> str:
        """Generate a hash for the content and attitude mode combination."""
        content = f"{text}:{attitude_mode}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def save_analysis(self, 
                     original_text: str, 
                     source_type: str,
                     analysis_result: Dict[str, Any],
                     attitude_mode: str,
                     llm_provider: str,
                     confidence_score: Optional[float] = None,
                     tags: Optional[List[str]] = None) -> int:
        """Save an analysis result to the database."""
        content_hash = self._generate_content_hash(original_text, attitude_mode)
        
        with sqlite3.connect(self.db_path) as conn:
            # Check if analysis already exists
            cursor = conn.execute(
                'SELECT id FROM analyses WHERE content_hash = ?',
                (content_hash,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing analysis
                analysis_id = existing[0]
                conn.execute('''
                    UPDATE analyses 
                    SET analysis_result = ?, 
                        llm_provider = ?, 
                        confidence_score = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (json.dumps(analysis_result), llm_provider, confidence_score, analysis_id))
            else:
                # Insert new analysis
                cursor = conn.execute('''
                    INSERT INTO analyses 
                    (content_hash, original_text, source_type, analysis_result, 
                     attitude_mode, llm_provider, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (content_hash, original_text, source_type, json.dumps(analysis_result),
                      attitude_mode, llm_provider, confidence_score))
                analysis_id = cursor.lastrowid
            
            # Handle tags
            if tags:
                # Remove existing tags
                conn.execute('DELETE FROM tags WHERE analysis_id = ?', (analysis_id,))
                # Add new tags
                for tag in tags:
                    conn.execute(
                        'INSERT INTO tags (analysis_id, tag) VALUES (?, ?)',
                        (analysis_id, tag.strip().lower())
                    )
            
            conn.commit()
            return analysis_id
    
    def get_analysis_by_hash(self, text: str, attitude_mode: str) -> Optional[Dict[str, Any]]:
        """Get an existing analysis by content hash."""
        content_hash = self._generate_content_hash(text, attitude_mode)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT *, 
                       GROUP_CONCAT(tags.tag) as tags_list
                FROM analyses 
                LEFT JOIN tags ON analyses.id = tags.analysis_id
                WHERE content_hash = ?
                GROUP BY analyses.id
            ''', (content_hash,))
            
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['analysis_result'] = json.loads(result['analysis_result'])
                result['tags'] = result['tags_list'].split(',') if result['tags_list'] else []
                del result['tags_list']
                return result
            return None
    
    def search_analyses(self, 
                       query: str = '',
                       attitude_mode: Optional[str] = None,
                       source_type: Optional[str] = None,
                       limit: int = 50,
                       offset: int = 0) -> List[Dict[str, Any]]:
        """Search analyses with optional filters."""
        conditions = []
        params = []
        
        if query:
            conditions.append('(original_text LIKE ? OR analysis_result LIKE ?)')
            params.extend([f'%{query}%', f'%{query}%'])
        
        if attitude_mode:
            conditions.append('attitude_mode = ?')
            params.append(attitude_mode)
        
        if source_type:
            conditions.append('source_type = ?')
            params.append(source_type)
        
        where_clause = 'WHERE ' + ' AND '.join(conditions) if conditions else ''
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(f'''
                SELECT analyses.*, 
                       GROUP_CONCAT(tags.tag) as tags_list
                FROM analyses 
                LEFT JOIN tags ON analyses.id = tags.analysis_id
                {where_clause}
                GROUP BY analyses.id
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', params + [limit, offset])
            
            results = []
            for row in cursor.fetchall():
                result = dict(row)
                result['analysis_result'] = json.loads(result['analysis_result'])
                result['tags'] = result['tags_list'].split(',') if result['tags_list'] else []
                del result['tags_list']
                results.append(result)
            
            return results
    
    def get_recent_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent analyses."""
        return self.search_analyses(limit=limit)
    
    def delete_analysis(self, analysis_id: int):
        """Delete an analysis and its tags."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM analyses WHERE id = ?', (analysis_id,))
            conn.commit()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT COUNT(*) as total_analyses FROM analyses')
            total = cursor.fetchone()[0]
            
            cursor = conn.execute('''
                SELECT attitude_mode, COUNT(*) as count 
                FROM analyses 
                GROUP BY attitude_mode
            ''')
            by_attitude = dict(cursor.fetchall())
            
            cursor = conn.execute('''
                SELECT source_type, COUNT(*) as count 
                FROM analyses 
                GROUP BY source_type
            ''')
            by_source = dict(cursor.fetchall())
            
            return {
                'total_analyses': total,
                'by_attitude_mode': by_attitude,
                'by_source_type': by_source
            }