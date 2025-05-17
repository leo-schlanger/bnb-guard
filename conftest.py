import warnings

def pytest_configure(config):
    # Supressão de DeprecationWarning vindo de websockets.legacy
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        module="websockets.legacy"
    )
