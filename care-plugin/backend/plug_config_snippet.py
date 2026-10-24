# Pattern from the Care plugin docs (docs.ohc.network/contributing/plugins) and the care_filly README.
# In the scaffold workflow, plugin registration is done through external config (see bootstrap.prompt.md),
# not by editing Care core. Use this as the content to register.
from plugs.plug import Plug

consultlens_plug = Plug(
    name="care_consultlens",
    package_name="care_consultlens",   # or git+https://github.com/<you>/care_consultlens.git
    version="",
    configs={
        "CONSULTLENS_API_URL": "http://host.docker.internal:8000",  # where the FastAPI service runs
    },
)

plugs = [consultlens_plug]
