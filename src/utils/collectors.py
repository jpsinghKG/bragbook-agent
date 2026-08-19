from pathlib import Path


def parse_identities(identities: str) -> list[str]:
    if not identities:
        return []
    return [identity.strip() for identity in identities.split(",")]

def parse_roots(roots: str) -> list[Path]:
    if not roots:
        return []
    return [Path(root.strip()).expanduser() for root in roots.split(",")]