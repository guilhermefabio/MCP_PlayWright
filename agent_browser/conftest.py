import pytest
from pathlib import Path
from utils.config import Config


@pytest.fixture(scope="session")
def config() -> Config:
    return Config()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True)
def screenshot_on_failure(request):
    yield
    if not (hasattr(request.node, "rep_call") and request.node.rep_call.failed):
        return
    page = request.node.funcargs.get("page")
    if page is None:
        return
    snapshot_dir = Path("tests/snapshots")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    safe_name = (
        request.node.nodeid
        .replace("/", "_")
        .replace("\\", "_")
        .replace("::", "_")
        .replace(".py", "")
        .replace("[", "_")
        .replace("]", "")
    )
    screenshot_path = snapshot_dir / f"{safe_name}.png"
    page.screenshot(path=str(screenshot_path))
    print(f"\nScreenshot salvo em: {screenshot_path}")
