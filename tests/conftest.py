from pathlib import Path
import pytest
import os


@pytest.fixture
def temp_cwd(tmp_path):
    """
    Fixture to change the current working directory to a temporary directory
    and then restore the original CWD after the test.
    """
    original_cwd = Path.cwd()  # Store the original CWD
    os.chdir(tmp_path)  # Change CWD to the temporary directory
    yield tmp_path  # Yield the temporary path for potential use in the test
    os.chdir(original_cwd)  # Restore the original CWD after the test
