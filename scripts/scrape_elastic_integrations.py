#!/usr/bin/env python3
"""
Elastic Integrations Scraper
Scrapes the elastic/integrations repository.
User controls which integrations to download via CSV is_enabled flag.
"""

import os
import sys
import csv
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Set

# Configuration - Always resolve paths relative to project root
PROJECT_ROOT = Path(os.path.dirname(os.path.abspath(__file__))).parent
ELASTIC_INTEGRATIONS_REPO = "https://github.com/elastic/integrations.git"
CLONE_DIR = PROJECT_ROOT / "data" / "integrations" / "repo"
CONFIG_CSV = PROJECT_ROOT / "data" / "integrations" / "elastic_integrations.csv"
SAMPLE_DIR = PROJECT_ROOT / "data" / "integrations" / "samples"

class ElasticIntegrationsScraper:
    def __init__(self):
        self.repo_path = Path(CLONE_DIR)
        self.config_csv = Path(CONFIG_CSV)
        self.sample_path = Path(SAMPLE_DIR)
        
        # Create necessary directories
        self.sample_path.mkdir(parents=True, exist_ok=True)
        
    def sync_repository(self) -> bool:
        """Sync elastic/integrations repository (clone or pull latest main)."""
        try:
            if self.repo_path.exists():
                print(f"Updating existing repository at {self.repo_path}")
                subprocess.run(
                    ["git", "-C", str(self.repo_path), "pull", "--ff-only", "origin", "main"],
                    check=True, capture_output=False, timeout=300
                )
            else:
                print(f"Cloning repository to {self.repo_path}")
                print("Performing fast shallow clone (main branch only)...")
                subprocess.run(
                    ["git", "clone", "--depth", "1", "--single-branch", "--branch", "main", 
                     ELASTIC_INTEGRATIONS_REPO, str(self.repo_path)],
                    check=True, capture_output=False, timeout=600
                )
            return True
        except Exception as e:
            print(f"Repository sync failed: {e}")
            return False
    
    def get_integration_names(self) -> List[str]:
        """Get all integration names from repository packages directory."""
        names = []
        packages_dir = self.repo_path / "packages"
        if packages_dir.exists() and packages_dir.is_dir():
            for package in packages_dir.iterdir():
                if package.is_dir():
                    names.append(package.name)
        return sorted(names)
    
    def init_config_csv(self) -> None:
        """Initialize configuration CSV with all integrations disabled by default."""
        if self.config_csv.exists():
            print(f"Config CSV already exists at {self.config_csv}")
            print("To refresh integration list delete this file first and re-run")
            return
        
        names = self.get_integration_names()
        if not names:
            print("No integrations found in repository")
            return
        
        # Write all entries with is_enabled=false
        with open(self.config_csv, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["name", "is_enabled"])
            for name in names:
                writer.writerow([name, "false"])
        
        print(f"Initialized config CSV with {len(names)} integrations")
        print(f"All integrations are set to false by default")
        print(f"Edit {self.config_csv} and set is_enabled=true for integrations you want to download")
    
    def read_config_csv(self) -> Set[str]:
        """Read CSV and return set of integrations marked as enabled."""
        enabled = set()
        if not self.config_csv.exists():
            return enabled
        
        with open(self.config_csv, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row.get("is_enabled", "false").lower() in ("true", "yes", "1"):
                    enabled.add(row["name"])
        return enabled
    
    def download_integration_sample(self, integration_name: str) -> bool:
        """Download sample_event.json for a single integration."""
        source_file = self.repo_path / "packages" / integration_name / "data_stream" / "package" / "sample_event.json"
        
        if not source_file.exists():
            # Check alternative locations
            found = False
            data_stream_dir = self.repo_path / "packages" / integration_name / "data_stream"
            if data_stream_dir.exists():
                for ds in data_stream_dir.iterdir():
                    if ds.is_dir():
                        test_file = ds / "sample_event.json"
                        if test_file.exists():
                            source_file = test_file
                            found = True
                            break
            if not found:
                return False
        
        target_dir = self.sample_path / integration_name
        target_dir.mkdir(exist_ok=True)
        target_file = target_dir / "sample_event.json"
        
        try:
            shutil.copy2(source_file, target_file)
            print(f"✓ Downloaded {integration_name}")
            return True
        except Exception as e:
            print(f"✗ Failed {integration_name}: {e}")
            return False
    
    def sync_enabled_samples(self) -> None:
        """Download samples for all integrations marked as enabled in CSV."""
        enabled = self.read_config_csv()
        if not enabled:
            print("No integrations marked as enabled in CSV")
            print(f"Edit {self.config_csv} to enable integrations")
            return
        
        print(f"\nFound {len(enabled)} integrations marked as enabled")
        print("Downloading sample_event.json files...\n")
        
        success = 0
        for name in sorted(enabled):
            if self.download_integration_sample(name):
                success +=1
        
        print(f"\nCompleted: {success}/{len(enabled)} samples downloaded")
    
    def run(self) -> None:
        """Run complete workflow."""
        print("Elastic Integrations Scraper")
        print("-" * 50)
        
        # Step 1: Sync repository
        if not self.sync_repository():
            sys.exit(1)
        
        print("\nRepository sync complete")
        
        # Step 2: Initialize config CSV if not exists
        self.init_config_csv()
        
        # Step 3: Sync enabled samples
        self.sync_enabled_samples()
        
        print("\nOperation completed successfully!")


if __name__ == "__main__":
    scraper = ElasticIntegrationsScraper()
    scraper.run()