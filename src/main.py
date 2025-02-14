import hydra
from omegaconf import DictConfig
import os
import logging
from typing import List
from mascarpone import Mascarpone
from hydra.core.hydra_config import HydraConfig

log = logging.getLogger(__name__)

def create_folders(cfg: DictConfig):
    """Create necessary folders for data and visualization output."""
    os.makedirs(cfg.save.folders.data, exist_ok=True)
    if cfg.save.enabled:
        os.makedirs(cfg.save.folders.static_vis, exist_ok=True)

def setup_environment(cfg: DictConfig):
    """Setup logging and create necessary folders."""
    logging.basicConfig(level=cfg.get("log_level", "INFO"))
    log.info(f"Working directory: {os.getcwd()}")
    create_folders(cfg)


@hydra.main(config_path="../config", config_name="config")
def main(cfg: DictConfig):
    """Main function to run the game analysis and visualization."""
    setup_environment(cfg)
    
    # Run game
    game = Mascarpone(cfg)
    game.play_game()
    
    # Return working directory for multirun
    return HydraConfig.get().run.dir

if __name__ == "__main__":
    main()