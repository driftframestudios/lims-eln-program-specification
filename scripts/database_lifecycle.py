"""Repository CLI for the installed Program-owned lifecycle admission API."""

from lims_eln_contracts.database_lifecycle import (
    AdmittedLifecycleProfile,
    CAPABILITY_SCHEMA_BYTES,
    CAPABILITY_SCHEMA_DIGEST,
    FindingCode,
    LifecycleAdmissionError,
    LifecycleSource,
    MAX_INPUT_BYTES,
    SCHEMA_BYTES,
    SCHEMA_DIGEST,
    SCHEMA_ID,
    admit_lifecycle_profile,
    main,
)


if __name__ == "__main__":
    raise SystemExit(main())
