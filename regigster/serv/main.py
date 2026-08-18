import logging
import subprocess
import sys
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


SCRIPTS = [
    os.path.join(os.path.dirname(__file__), "select_top_models.py"),
    os.path.join(os.path.dirname(__file__), "register_models.py"),
    os.path.join(os.path.dirname(__file__), "promote_best_model.py"),
]


def run_script(script_name):

    logger.info("Starting: %s", script_name)

    result = subprocess.run(
        [sys.executable, script_name],
        check=False
    )

    if result.returncode != 0:
        logger.error(
            "Failed: %s | exit_code=%s",
            script_name,
            result.returncode
        )
        raise RuntimeError(
            f"{script_name} failed"
        )

    logger.info(
        "Completed: %s",
        script_name
    )


def main():

    logger.info("===== MLflow Model Pipeline Started =====")

    for script in SCRIPTS:
        run_script(script)

    logger.info("===== MLflow Model Pipeline Completed =====")


if __name__ == "__main__":
    main()