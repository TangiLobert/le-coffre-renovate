from src.domain.setup_info import SetupInfo


def setup_master_password(setup_info: SetupInfo | None, password: str) -> SetupInfo:
    if setup_info is not None:
        raise Exception("Already setup")

    password_hash = "hashed_" + password  # Replace with real hash logic
    return SetupInfo(password_hash=password_hash)
