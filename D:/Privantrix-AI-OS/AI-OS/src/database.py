"""
Privantrix AI OS - Database Manager
Production-grade SQLite and ChromaDB initialization and management
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from contextlib import contextmanager
import json


class DatabaseManager:
    """Manages SQLite database initialization and operations"""
    
    def __init__(self, db_path: str = "database/privantrix.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._engine = None
        self._session_factory = None
    
    def initialize(self) -> None:
        """Initialize the database with all tables"""
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker, declarative_base
        
        # Create engine with optimizations
        self._engine = create_engine(
            f"sqlite:///{self.db_path}",
            echo=False,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False}
        )
        
        # Create all tables
        Base = declarative_base()
        Base.metadata.create_all(self._engine)
        
        # Create session factory
        self._session_factory = sessionmaker(bind=self._engine, autocommit=False, autoflush=False)
        
        # Run migrations
        self._run_migrations()
    
    def _run_migrations(self) -> None:
        """Run database migrations"""
        from sqlalchemy import text
        
        with self.get_session() as session:
            # Create projects table
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    metadata JSON
                )
            """))
            
            # Create tasks table
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    priority INTEGER DEFAULT 0,
                    assigned_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    metadata JSON,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
            """))
            
            # Create agents table
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL,
                    status TEXT DEFAULT 'idle',
                    capabilities JSON,
                    current_task_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create workflows table
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    steps JSON,
                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSON
                )
            """))
            
            # Create checkpoints table
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    checkpoint_type TEXT NOT NULL,
                    data JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSON
                )
            """))
            
            # Create memory_entries table
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding_ref TEXT,
                    metadata JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    importance_score REAL DEFAULT 0.0
                )
            """))
            
            # Create model_configs table
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS model_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    endpoint TEXT,
                    capabilities JSON,
                    priority INTEGER DEFAULT 0,
                    context_length INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    metadata JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create logs table
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    source TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSON
                )
            """))
            
            # Create indexes
            session.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id)"))
            session.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)"))
            session.execute(text("CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_entries(entry_type)"))
            session.execute(text("CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level)"))
            session.execute(text("CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)"))
            
            session.commit()
    
    @contextmanager
    def get_session(self):
        """Get a database session context manager"""
        if self._session_factory is None:
            self.initialize()
        
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute a raw SQL query"""
        from sqlalchemy import text
        
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a record into a table"""
        from sqlalchemy import text
        
        with self.get_session() as session:
            columns = ', '.join(data.keys())
            placeholders = ', '.join([f':{k}' for k in data.keys()])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            result = session.execute(text(query), data)
            session.commit()
            return result.lastrowid or 0
    
    def update(self, table: str, data: Dict[str, Any], where: str, where_params: Dict[str, Any]) -> int:
        """Update records in a table"""
        from sqlalchemy import text
        
        with self.get_session() as session:
            set_clause = ', '.join([f"{k} = :{k}" for k in data.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE {where}"
            
            params = {**data, **where_params}
            result = session.execute(text(query), params)
            session.commit()
            return result.rowcount
    
    def delete(self, table: str, where: str, where_params: Dict[str, Any]) -> int:
        """Delete records from a table"""
        from sqlalchemy import text
        
        with self.get_session() as session:
            query = f"DELETE FROM {table} WHERE {where}"
            result = session.execute(text(query), where_params)
            session.commit()
            return result.rowcount
    
    def select(self, table: str, columns: Optional[List[str]] = None, 
               where: Optional[str] = None, where_params: Optional[Dict] = None,
               order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """Select records from a table"""
        from sqlalchemy import text
        
        col_str = ', '.join(columns) if columns else '*'
        query = f"SELECT {col_str} FROM {table}"
        
        params = {}
        if where:
            query += f" WHERE {where}"
            params = where_params or {}
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query, params if params else None)
    
    def backup(self, backup_path: str) -> str:
        """Create a database backup"""
        import shutil
        from datetime import datetime
        
        backup_file = Path(backup_path) / f"privantrix_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(self.db_path, backup_file)
        return str(backup_file)
    
    def restore(self, backup_path: str) -> None:
        """Restore database from backup"""
        import shutil
        shutil.copy2(backup_path, self.db_path)


class ChromaDBManager:
    """Manages ChromaDB vector store initialization and operations"""
    
    def __init__(self, persist_dir: str = "embeddings/chroma_db"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = None
        self._collections = {}
    
    def initialize(self) -> None:
        """Initialize ChromaDB client"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            self._client = chromadb.Client(Settings(
                persist_directory=str(self.persist_dir),
                anonymized_telemetry=False
            ))
        except ImportError:
            raise ImportError("ChromaDB not installed. Install with: pip install chromadb")
    
    def get_client(self):
        """Get ChromaDB client"""
        if self._client is None:
            self.initialize()
        return self._client
    
    def get_or_create_collection(self, name: str, **kwargs) -> Any:
        """Get or create a collection"""
        if self._client is None:
            self.initialize()
        
        if name not in self._collections:
            self._collections[name] = self._client.get_or_create_collection(name=name, **kwargs)
        
        return self._collections[name]
    
    def add_embedding(self, collection_name: str, documents: List[str], 
                      embeddings: Optional[List[List[float]]] = None,
                      metadatas: Optional[List[Dict]] = None,
                      ids: Optional[List[str]] = None) -> None:
        """Add embeddings to a collection"""
        collection = self.get_or_create_collection(collection_name)
        
        if ids is None:
            import hashlib
            import time
            ids = [hashlib.md5(f"{doc}{time.time()}".encode()).hexdigest() for doc in documents]
        
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def query_embeddings(self, collection_name: str, query_texts: List[str], 
                         n_results: int = 5,
                         where: Optional[Dict] = None) -> Dict:
        """Query embeddings from a collection"""
        collection = self.get_or_create_collection(collection_name)
        
        return collection.query(
            query_texts=query_texts,
            n_results=n_results,
            where=where
        )
    
    def delete_collection(self, name: str) -> None:
        """Delete a collection"""
        if self._client is None:
            self.initialize()
        
        self._client.delete_collection(name=name)
        if name in self._collections:
            del self._collections[name]
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        if self._client is None:
            self.initialize()
        
        return [c.name for c in self._client.list_collections()]
    
    def get_collection_count(self, name: str) -> int:
        """Get the number of items in a collection"""
        collection = self.get_or_create_collection(name)
        return collection.count()


def init_database(db_path: str = "database/privantrix.db") -> DatabaseManager:
    """Initialize SQLite database"""
    db = DatabaseManager(db_path)
    db.initialize()
    return db


def init_chromadb(persist_dir: str = "embeddings/chroma_db") -> ChromaDBManager:
    """Initialize ChromaDB"""
    chroma = ChromaDBManager(persist_dir)
    chroma.initialize()
    return chroma


def init_all_databases(base_dir: str = "D:/Privantrix-AI-OS/AI-OS") -> tuple:
    """Initialize all databases"""
    os.chdir(base_dir)
    
    db = init_database("database/privantrix.db")
    chroma = init_chromadb("embeddings/chroma_db")
    
    return db, chroma
