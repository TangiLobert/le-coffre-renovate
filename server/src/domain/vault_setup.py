from src.domain.setup_info import SetupInfo


def setup_master_password(
    setup_info: SetupInfo | None, nb_shared: int, threshold: int
) -> SetupInfo:
    if setup_info is not None:
        raise Exception("Already setup")
    if nb_shared < 2:
        raise Exception("Number of shares must be at least 2")
    if threshold < 2:
        raise Exception("Threshold must be at least 2")
    if threshold > nb_shared:
        raise Exception("Threshold cannot be greater than number of shares")

    password_hash = (
        f"hashed_{nb_shared}_{threshold}"  # Replace with shamir secret sharing logic
    )
    return SetupInfo(password_hash=password_hash)
