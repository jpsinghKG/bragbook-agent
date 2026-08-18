from collectors.git_local.git_local import collect
from pathlib import Path
from datetime import datetime, timedelta

if __name__ == "__main__":
    roots = [Path("/Users/jpsingh/Documents/KG/POCs")]
    identities = ["jpsingh"]
    since = datetime.today() - timedelta(days=1)
    until = datetime.today() + timedelta(days=1)
    include_patch = False
    events = collect(roots, identities, since, until, include_patch)
    print(len(events))
