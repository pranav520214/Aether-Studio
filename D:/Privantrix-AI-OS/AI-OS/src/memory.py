"""
Privantrix AI OS - Memory Manager
Production-grade memory management with multiple storage backends
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum


class MemoryType(Enum):
    WORKING = "working"
    SESSION = "session"
    PROJECT = "project"
    LONG_TERM = "long_term"
    KNOWLEDGE = "knowledge"
    VECTOR = "vector"


@dataclass
class MemoryEntry:
    id: str = ""
    content: str = ""
    memory_type: MemoryType = MemoryType.WORKING
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    importance_score: float = 0.0
    access_count: int = 0
    created_at: str = ""
    updated_at: str = ""
    last_accessed: str = ""
    expires_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = hashlib.md5(f"{self.content}{datetime.now()}".encode()).hexdigest()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WorkingMemory:
    def __init__(self, max_entries: int = 100):
        self.max_entries = max_entries
        self._entries: Dict[str, MemoryEntry] = {}
        self._access_order: List[str] = []
    
    def add(self, entry: MemoryEntry) -> str:
        entry.memory_type = MemoryType.WORKING
        while len(self._entries) >= self.max_entries and self._access_order:
            oldest_id = self._access_order.pop(0)
            if oldest_id in self._entries:
                del self._entries[oldest_id]
        self._entries[entry.id] = entry
        self._access_order.append(entry.id)
        return entry.id
    
    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        if entry_id in self._entries:
            entry = self._entries[entry_id]
            entry.access_count += 1
            entry.last_accessed = datetime.now().isoformat()
            if entry_id in self._access_order:
                self._access_order.remove(entry_id)
            self._access_order.append(entry_id)
            return entry
        return None
    
    def search(self, query: str) -> List[MemoryEntry]:
        results = []
        query_lower = query.lower()
        for entry in self._entries.values():
            if query_lower in entry.content.lower():
                results.append(entry)
        return sorted(results, key=lambda e: e.access_count, reverse=True)
    
    def clear(self) -> None:
        self._entries.clear()
        self._access_order.clear()
    
    def size(self) -> int:
        return len(self._entries)


class SessionMemory:
    def __init__(self, ttl_hours: int = 24):
        self.ttl_hours = ttl_hours
        self._entries: Dict[str, MemoryEntry] = {}
    
    def add(self, entry: MemoryEntry) -> str:
        entry.memory_type = MemoryType.SESSION
        entry.expires_at = (datetime.now() + timedelta(hours=self.ttl_hours)).isoformat()
        self._entries[entry.id] = entry
        return entry.id
    
    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        if entry_id not in self._entries:
            return None
        entry = self._entries[entry_id]
        if entry.expires_at:
            expires = datetime.fromisoformat(entry.expires_at)
            if datetime.now() > expires:
                del self._entries[entry_id]
                return None
        entry.access_count += 1
        entry.last_accessed = datetime.now().isoformat()
        return entry
    
    def cleanup_expired(self) -> int:
        expired = []
        now = datetime.now()
        for entry_id, entry in self._entries.items():
            if entry.expires_at:
                expires = datetime.fromisoformat(entry.expires_at)
                if now > expires:
                    expired.append(entry_id)
        for entry_id in expired:
            del self._entries[entry_id]
        return len(expired)
    
    def get_all(self) -> List[MemoryEntry]:
        self.cleanup_expired()
        return list(self._entries.values())


class ProjectMemory:
    def __init__(self, projects_dir: str = "projects"):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self._current_project: Optional[str] = None
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def set_project(self, project_name: str) -> None:
        self._current_project = project_name
        project_file = self.projects_dir / f"{project_name}.json"
        if project_file.exists():
            with open(project_file, 'r') as f:
                self._cache[project_name] = json.load(f)
        else:
            self._cache[project_name] = {"metadata": {}, "tasks": [], "notes": [], "checkpoints": []}
    
    def save(self) -> None:
        if self._current_project and self._current_project in self._cache:
            project_file = self.projects_dir / f"{self._current_project}.json"
            with open(project_file, 'w') as f:
                json.dump(self._cache[self._current_project], f, indent=2)
    
    def add_task(self, task: Dict[str, Any]) -> str:
        task_id = hashlib.md5(f"{task}{datetime.now()}".encode()).hexdigest()
        task["id"] = task_id
        task["created_at"] = datetime.now().isoformat()
        if self._current_project and self._current_project in self._cache:
            self._cache[self._current_project]["tasks"].append(task)
            self.save()
        return task_id
    
    def add_note(self, note: str, tags: Optional[List[str]] = None) -> str:
        note_id = hashlib.md5(f"{note}{datetime.now()}".encode()).hexdigest()
        note_entry = {"id": note_id, "content": note, "tags": tags or [], "created_at": datetime.now().isoformat()}
        if self._current_project and self._current_project in self._cache:
            self._cache[self._current_project]["notes"].append(note_entry)
            self.save()
        return note_id
    
    def get_tasks(self, status: Optional[str] = None) -> List[Dict]:
        if not self._current_project or self._current_project not in self._cache:
            return []
        tasks = self._cache[self._current_project].get("tasks", [])
        if status:
            tasks = [t for t in tasks if t.get("status") == status]
        return tasks
    
    def add_checkpoint(self, checkpoint_data: Dict[str, Any]) -> str:
        checkpoint_id = hashlib.md5(f"{checkpoint_data}{datetime.now()}".encode()).hexdigest()
        checkpoint = {"id": checkpoint_id, "data": checkpoint_data, "timestamp": datetime.now().isoformat()}
        if self._current_project and self._current_project in self._cache:
            self._cache[self._current_project]["checkpoints"].append(checkpoint)
            self.save()
        return checkpoint_id


class LongTermMemory:
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self._index_file = self.memory_dir / "index.json"
        self._index: Dict[str, Dict[str, Any]] = {}
        self._load_index()
    
    def _load_index(self) -> None:
        if self._index_file.exists():
            with open(self._index_file, 'r') as f:
                self._index = json.load(f)
    
    def _save_index(self) -> None:
        with open(self._index_file, 'w') as f:
            json.dump(self._index, f, indent=2)
    
    def store(self, key: str, data: Any, compress: bool = True) -> str:
        entry_id = hashlib.md5(f"{key}{datetime.now()}".encode()).hexdigest()
        file_path = self.memory_dir / f"{entry_id}.json"
        memory_entry = {"id": entry_id, "key": key, "data": data, "compressed": compress, "created_at": datetime.now().isoformat(), "access_count": 0}
        with open(file_path, 'w') as f:
            json.dump(memory_entry, f)
        self._index[key] = {"id": entry_id, "file": str(file_path), "created_at": memory_entry["created_at"]}
        self._save_index()
        return entry_id
    
    def retrieve(self, key: str) -> Optional[Any]:
        if key not in self._index:
            return None
        file_path = Path(self._index[key]["file"])
        if not file_path.exists():
            return None
        with open(file_path, 'r') as f:
            entry = json.load(f)
        entry["access_count"] += 1
        entry["last_accessed"] = datetime.now().isoformat()
        with open(file_path, 'w') as f:
            json.dump(entry, f)
        self._index[key]["last_accessed"] = entry["last_accessed"]
        self._save_index()
        return entry["data"]
    
    def search(self, query: str) -> List[Dict]:
        results = []
        query_lower = query.lower()
        for entry_id, index_entry in self._index.items():
            file_path = Path(index_entry["file"])
            if file_path.exists():
                with open(file_path, 'r') as f:
                    entry = json.load(f)
                searchable = f"{entry['key']} {json.dumps(entry['data'])}".lower()
                if query_lower in searchable:
                    results.append({"key": entry["key"], "data": entry["data"], "access_count": entry.get("access_count", 0)})
        return sorted(results, key=lambda r: r["access_count"], reverse=True)


class KnowledgeGraph:
    def __init__(self):
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._edges: List[Dict[str, Any]] = []
    
    def add_node(self, node_id: str, node_type: str, properties: Dict[str, Any]) -> None:
        self._nodes[node_id] = {"id": node_id, "type": node_type, "properties": properties, "created_at": datetime.now().isoformat()}
    
    def add_edge(self, source_id: str, target_id: str, relation: str, properties: Optional[Dict[str, Any]] = None) -> None:
        self._edges.append({"source": source_id, "target": target_id, "relation": relation, "properties": properties or {}, "created_at": datetime.now().isoformat()})
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        return self._nodes.get(node_id)
    
    def get_neighbors(self, node_id: str, relation: Optional[str] = None) -> List[Dict]:
        neighbors = []
        for edge in self._edges:
            if edge["source"] == node_id or edge["target"] == node_id:
                if relation is None or edge["relation"] == relation:
                    neighbor_id = edge["target"] if edge["source"] == node_id else edge["source"]
                    if neighbor_id in self._nodes:
                        neighbor = self._nodes[neighbor_id].copy()
                        neighbor["relation"] = edge["relation"]
                        neighbors.append(neighbor)
        return neighbors
    
    def to_dict(self) -> Dict[str, Any]:
        return {"nodes": list(self._nodes.values()), "edges": self._edges}


class MemoryManager:
    def __init__(self, base_dir: str = "D:/Privantrix-AI-OS/AI-OS"):
        os.chdir(base_dir)
        self.working = WorkingMemory()
        self.session = SessionMemory()
        self.project = ProjectMemory()
        self.long_term = LongTermMemory()
        self.knowledge_graph = KnowledgeGraph()
    
    def add_to_memory(self, content: str, memory_type: MemoryType = MemoryType.WORKING, metadata: Optional[Dict] = None) -> str:
        entry = MemoryEntry(content=content, memory_type=memory_type, metadata=metadata or {})
        if memory_type == MemoryType.WORKING:
            return self.working.add(entry)
        elif memory_type == MemoryType.SESSION:
            return self.session.add(entry)
        else:
            return self.long_term.store(hashlib.md5(content.encode()).hexdigest(), entry.to_dict())
    
    def search_memory(self, query: str) -> List[Dict]:
        results = []
        working_results = self.working.search(query)
        results.extend([{"type": "working", **r.to_dict()} for r in working_results])
        long_term_results = self.long_term.search(query)
        results.extend([{"type": "long_term", **r} for r in long_term_results])
        return results
    
    def get_context(self, max_entries: int = 10) -> str:
        entries = list(self.working._entries.values())[-max_entries:]
        return "\n".join([e.content for e in entries])
    
    def save_checkpoint(self, name: str, data: Dict[str, Any]) -> str:
        return self.long_term.store(f"checkpoint_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}", data)


def init_memory(base_dir: str = "D:/Privantrix-AI-OS/AI-OS") -> MemoryManager:
    manager = MemoryManager(base_dir)
    return manager
