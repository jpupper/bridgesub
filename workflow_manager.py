import json
import os
from pathlib import Path

class WorkflowManager:
    def __init__(self, workflows_dir="workflows"):
        self.workflows_dir = workflows_dir
        Path(workflows_dir).mkdir(exist_ok=True)
    
    def save_workflow(self, name, subtitle_configs):
        """Save a workflow configuration"""
        workflow_data = {
            "name": name,
            "configs": []
        }
        
        for config in subtitle_configs:
            config_data = {
                "language": config.language_var.get(),
                "color": config.color_var.get(),
                "font_size": config.fontsize_var.get(),
                "y_position": config.ypos_var.get()
            }
            workflow_data["configs"].append(config_data)
        
        file_path = Path(self.workflows_dir) / f"{name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(workflow_data, f, indent=4)
    
    def load_workflow(self, name):
        """Load a workflow configuration"""
        file_path = Path(self.workflows_dir) / f"{name}.json"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def list_workflows(self):
        """List all available workflows"""
        return [f.stem for f in Path(self.workflows_dir).glob("*.json")]
    
    def delete_workflow(self, name):
        """Delete a workflow"""
        file_path = Path(self.workflows_dir) / f"{name}.json"
        try:
            file_path.unlink()
            return True
        except FileNotFoundError:
            return False
