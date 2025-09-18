# code/config/settings.py

# Configuration settings
"""
Configuration management for MCP Data Visualization Server
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr

PROJECT_ROOT = Path(__file__).parent.parent.parent
# print(f"Project root set to: {PROJECT_ROOT}")


class FigureSizeConfig(BaseSettings):
    """Figure size configuration for visualizations"""

    width: int = Field(default=800, env="VIZ_WIDTH")
    height: int = Field(default=600, env="VIZ_HEIGHT")


class ChartDefaultsBar(BaseSettings):
    orientation: Literal["v", "h"] = "v"
    text_auto: bool = True
    show_legend: bool = True


class ChartDefaultsLine(BaseSettings):
    mode: str = "lines+markers"
    line_width: int = 2
    marker_size: int = 6


class ChartDefaultsScatter(BaseSettings):
    mode: str = "markers"
    marker_size: int = 8
    opacity: float = 0.7


class ChartDefaultsPie(BaseSettings):
    hole: float = 0.0
    text_info: str = "label+percent"


class ChartDefaultsHistogram(BaseSettings):
    bins: int = 30
    opacity: float = 0.7
    show_distribution: bool = True


class ChartDefaultsConfig(BaseSettings):
    """Default settings for various chart types"""

    bar: ChartDefaultsBar = ChartDefaultsBar()
    line: ChartDefaultsLine = ChartDefaultsLine()
    scatter: ChartDefaultsScatter = ChartDefaultsScatter()
    pie: ChartDefaultsPie = ChartDefaultsPie()
    histogram: ChartDefaultsHistogram = ChartDefaultsHistogram()


class VisualizationConfig(BaseSettings):
    """Visualization configuration"""

    default_theme: str = Field(default="plotly_white", env="VIZ_THEME")
    output_format: str = "html"
    figure_size: FigureSizeConfig = FigureSizeConfig()
    color_schemes: Dict[str, Any] = {
        "categorical": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
        "sequential": "Blues",
        "diverging": "RdBu",
    }
    chart_defaults: ChartDefaultsConfig = ChartDefaultsConfig()
    max_rows_for_charts: int = Field(
        default=100000,
        description="Maximum rows to load into memory for chart generation to avoid OOM.",
    )
    width: int = 500
    height: int = 300


class SamplingConfig(BaseSettings):
    """Data sampling configuration"""

    large_dataset_threshold: int = 100000
    sample_size: int = 10000
    sampling_method: Literal["random", "systematic", "stratified"] = "random"


class DataConfig(BaseSettings):
    """Data Processing Configuration"""

    max_rows_preview: int = 1000
    max_file_size_mb: int = 100
    supported_formats: List[str] = ["csv", "parquet", "json", "xlsx"]
    sampling: SamplingConfig = SamplingConfig()


# --- Main Settings Class ---
class Settings(BaseSettings):
    """Main settings class"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        # Added yaml_file and yaml_file_encoding to enable automatic loading
        yaml_file="config.yaml",
        yaml_file_encoding="utf-8",
    )
    visualization: VisualizationConfig = VisualizationConfig()


# --- Config Manager to handle YAML and Pydantic ---
_config_manager_logger = logging.getLogger(__name__ + ".ConfigManager")


class ConfigManager:
    """
    Configuration manager that loads settings via Pydantic's BaseSettings.
    It relies on BaseSettings's `model_config` to handle environment variables and YAML files.
    """

    def __init__(self):
        self._settings: Optional[Settings] = Settings()

    def get_settings(self) -> Settings:
        """
        Retrieves the application settings.
        Settings are loaded (or reloaded) using Pydantic's built-in mechanisms
        which consult environment variables and the configured YAML file.
        """
        return self._settings

    def reload(self):
        """
        Forces a reload of configuration on the next call to get_settings().
        This clears the cached settings object.
        """
        self._settings = None
        _config_manager_logger.info("Configuration marked for reload.")


# Global configuration instance
config_manager = ConfigManager()


def get_server_config() -> Settings:
    """
    Convenience function to get server configuration.
    Returns the complete Settings object.
    """
    return config_manager.get_settings()


def get_visualization_config() -> VisualizationConfig:
    """
    Convenience function to get visualization configuration.
    """
    return config_manager.get_settings().visualization
