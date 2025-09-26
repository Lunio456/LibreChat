# config.py
from pathlib import Path
from typing import Literal, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class FigureSizeConfig(BaseSettings):
    width: int = 800
    height: int = 600


class ChartDefaults(BaseSettings):
    bar_orientation: Literal["v", "h"] = "v"
    line_mode: str = "lines+markers"
    scatter_mode: str = "markers"
    pie_hole: float = 0.4
    histogram_bins: int = 30


class SamplingConfig(BaseSettings):
    enabled: bool = True
    large_dataset_threshold: int = 50000
    sample_size: int = 10000
    method: Literal["random", "systematic", "stratified"] = "random"


class VisualizationConfig(BaseSettings):
    default_theme: str = "plotly_white"
    figure_size: FigureSizeConfig = FigureSizeConfig()
    chart_defaults: ChartDefaults = ChartDefaults()
    sampling: SamplingConfig = SamplingConfig()
    max_rows_for_charts: int = 100000


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        yaml_file="config.yaml",
        yaml_file_encoding="utf-8",
    )
    visualization: VisualizationConfig = VisualizationConfig()


class ConfigManager:
    _settings: Optional[Settings] = None

    def get(self) -> Settings:
        if self._settings is None:
            self._settings = Settings()
        return self._settings

    def reload(self):
        self._settings = None


config_manager = ConfigManager()

def get_visualization_config() -> VisualizationConfig:
    return config_manager.get().visualization
