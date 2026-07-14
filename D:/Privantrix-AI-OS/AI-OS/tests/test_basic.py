#!/usr/bin/env python3
"""
Privantrix AI OS - Basic Tests
"""

import pytest
from pathlib import Path


class TestDirectoryStructure:
    """Test that required directories exist"""
    
    def test_base_directory_exists(self):
        base = Path(__file__).parent.parent
        assert base.exists()
    
    def test_src_directory_exists(self):
        src = Path(__file__).parent.parent / "src"
        assert src.exists()
    
    def test_configs_directory_exists(self):
        configs = Path(__file__).parent.parent / "configs"
        assert configs.exists()
    
    def test_database_directory_exists(self):
        database = Path(__file__).parent.parent / "database"
        assert database.exists()


class TestSourceModules:
    """Test that source modules can be imported"""
    
    def test_config_module(self):
        from src import config
        assert hasattr(config, 'ConfigurationManager')
        assert hasattr(config, 'PrivantrixConfig')
    
    def test_hardware_module(self):
        from src import hardware
        assert hasattr(hardware, 'HardwareDetector')
        assert hasattr(hardware, 'SystemInfo')
    
    def test_memory_module(self):
        from src import memory
        assert hasattr(memory, 'MemoryManager')
        assert hasattr(memory, 'WorkingMemory')
    
    def test_router_module(self):
        from src import router
        assert hasattr(router, 'ModelRouter')
        assert hasattr(router, 'RegisteredModel')
    
    def test_planner_module(self):
        from src import planner
        assert hasattr(planner, 'Planner')
        assert hasattr(planner, 'Task')
    
    def test_lmstudio_module(self):
        from src import lmstudio
        assert hasattr(lmstudio, 'LMStudioClient')
        assert hasattr(lmstudio, 'CompletionResponse')
    
    def test_logging_module(self):
        from src import logging as privantrix_logging
        assert hasattr(privantrix_logging, 'PrivantrixLogger')
        assert hasattr(privantrix_logging, 'init_logging')
    
    def test_database_module(self):
        from src import database
        assert hasattr(database, 'DatabaseManager')
        assert hasattr(database, 'ChromaDBManager')


class TestConfiguration:
    """Test configuration system"""
    
    def test_default_config_creation(self):
        from src.config import ConfigurationManager, PrivantrixConfig
        manager = ConfigurationManager()
        config = PrivantrixConfig()
        assert config.base_dir is not None
        assert config.environment in ["development", "staging", "production"]


class TestMemoryComponents:
    """Test memory components"""
    
    def test_working_memory_add_get(self):
        from src.memory import WorkingMemory, MemoryEntry, MemoryType
        
        wm = WorkingMemory(max_entries=10)
        entry = MemoryEntry(content="test content", memory_type=MemoryType.WORKING)
        entry_id = wm.add(entry)
        
        retrieved = wm.get(entry_id)
        assert retrieved is not None
        assert retrieved.content == "test content"
    
    def test_working_memory_search(self):
        from src.memory import WorkingMemory, MemoryEntry, MemoryType
        
        wm = WorkingMemory(max_entries=10)
        wm.add(MemoryEntry(content="hello world", memory_type=MemoryType.WORKING))
        wm.add(MemoryEntry(content="foo bar", memory_type=MemoryType.WORKING))
        
        results = wm.search("hello")
        assert len(results) == 1
        assert results[0].content == "hello world"


class TestRouter:
    """Test model router"""
    
    def test_register_model(self):
        from src.router import ModelRouter
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "models.json")
            router = ModelRouter(config_path)
            
            model = router.register_model(
                model_id="test-model",
                name="Test Model",
                endpoint="http://localhost:1234",
                capabilities=["chat", "completion"]
            )
            
            assert model.id == "test-model"
            assert model.name == "Test Model"
    
    def test_select_model(self):
        from src.router import ModelRouter
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "models.json")
            router = ModelRouter(config_path)
            
            router.register_model("model1", "Model One", "http://localhost:1234", priority=1)
            router.register_model("model2", "Model Two", "http://localhost:1235", priority=2)
            
            selected = router.select_model()
            assert selected is not None
            assert selected.id == "model2"  # Higher priority


class TestPlanner:
    """Test planner functionality"""
    
    def test_create_task(self):
        from src.planner import Planner, TaskStatus
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            planner = Planner(memory_dir=tmpdir, checkpoints_dir=tmpdir)
            
            task_id = planner.create_task(
                title="Test Task",
                description="A test task"
            )
            
            assert task_id is not None
            pending = planner.get_pending_tasks()
            assert len(pending) == 1
            assert pending[0].title == "Test Task"
    
    def test_task_status_update(self):
        from src.planner import Planner, TaskStatus
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            planner = Planner(memory_dir=tmpdir, checkpoints_dir=tmpdir)
            
            task_id = planner.create_task("Test", "Description")
            success = planner.update_task_status(task_id, TaskStatus.IN_PROGRESS)
            
            assert success
            in_progress = planner.get_in_progress_tasks()
            assert len(in_progress) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
