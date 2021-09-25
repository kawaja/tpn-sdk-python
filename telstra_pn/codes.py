import enum


class status(enum.Enum):
    active = 1
    inactive = 2
    expired = 3
    deleted = 4
    suspend = 5
    new = 6
    deploying = 7
    deployed = 8
    deleting = 9
    expiring = 10
    updating = 11
    failed = 12


class vportstatus(enum.Enum):
    deployed = 'Deployed'
    deleted = 'Deleted'


class topologystatus(enum.Enum):
    active = 'active'


class latency(enum.Enum):
    low = 1
    standard = 2
    best_effort = 3


class renewal(enum.Enum):
    auto_disconnect = 0
    auto_renew = 1
    pay_by_hour = 2
    pay_by_month = 3


class vnf_status(enum.Enum):
    active = 'ACTIVE'
    build = 'BUILD'
    shutoff = 'SHUTOFF'
    verify_resize = 'VERIFY_RESIZE'
    paused = 'PAUSED'
    suspended = 'SUSPENDED'
    rescue = 'RESCUE'
    error = 'ERROR'
    deleted = 'DELETED'
    soft_deleted = 'SOFT_DELETED'
    shelved = 'SHELVED'
    shelved_offloaded = 'SHELVED_OFFLOADED'


class vnf_backup_status(enum.Enum):
    creating = 'CRG'
    created = 'CRE'
    deleting = 'DLG'
    deleted = 'DEL'
    restoring = 'REG'
    active = 'ACT'
    error = 'ERR'
