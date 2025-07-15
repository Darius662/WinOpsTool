"""Configuration schema for the Windows System Management Tool."""

CONFIG_SCHEMA = {
    "environment_variables": {
        "system": {
            "type": "dict",
            "description": "System environment variables to set"
        },
        "user": {
            "type": "dict",
            "description": "User environment variables to set"
        }
    },
    "registry": {
        "keys": {
            "type": "list",
            "items": {
                "type": "dict",
                "schema": {
                    "path": {"type": "string"},
                    "values": {
                        "type": "list",
                        "items": {
                            "type": "dict",
                            "schema": {
                                "name": {"type": "string"},
                                "type": {"type": "string", "allowed": ["REG_SZ", "REG_DWORD", "REG_BINARY", "REG_MULTI_SZ"]},
                                "value": {"type": "any"}
                            }
                        }
                    }
                }
            }
        }
    },
    "users_and_groups": {
        "users": {
            "type": "list",
            "items": {
                "type": "dict",
                "schema": {
                    "name": {"type": "string"},
                    "password": {"type": "string"},
                    "groups": {"type": "list", "items": {"type": "string"}},
                    "comment": {"type": "string"},
                    "flags": {"type": "integer"}
                }
            }
        },
        "groups": {
            "type": "list",
            "items": {
                "type": "dict",
                "schema": {
                    "name": {"type": "string"},
                    "comment": {"type": "string"},
                    "members": {"type": "list", "items": {"type": "string"}}
                }
            }
        }
    },
    "services": {
        "type": "list",
        "items": {
            "type": "dict",
            "schema": {
                "name": {"type": "string"},
                "start_type": {"type": "string", "allowed": ["auto", "manual", "disabled"]},
                "state": {"type": "string", "allowed": ["start", "stop", "restart"]},
                "description": {"type": "string"}
            }
        }
    },
    "firewall": {
        "rules": {
            "type": "list",
            "items": {
                "type": "dict",
                "schema": {
                    "name": {"type": "string"},
                    "direction": {"type": "string", "allowed": ["in", "out"]},
                    "action": {"type": "string", "allowed": ["allow", "block"]},
                    "protocol": {"type": "string"},
                    "local_ports": {"type": "list", "items": {"type": "string"}},
                    "remote_ports": {"type": "list", "items": {"type": "string"}},
                    "enabled": {"type": "boolean"}
                }
            }
        }
    },
    "software": {
        "install": {
            "type": "list",
            "items": {
                "type": "dict",
                "schema": {
                    "name": {"type": "string"},
                    "path": {"type": "string"},
                    "arguments": {"type": "string"},
                    "type": {"type": "string", "allowed": ["msi", "exe"]},
                    "verify_installed": {"type": "string", "description": "Registry key or file path to verify installation"}
                }
            }
        },
        "uninstall": {
            "type": "list",
            "items": {"type": "string", "description": "Names of software to uninstall"}
        }
    },
    "permissions": {
        "type": "list",
        "items": {
            "type": "dict",
            "schema": {
                "path": {"type": "string"},
                "permissions": {
                    "type": "list",
                    "items": {
                        "type": "dict",
                        "schema": {
                            "user": {"type": "string"},
                            "rights": {"type": "list", "items": {"type": "string"}},
                            "inheritance": {"type": "boolean"}
                        }
                    }
                }
            }
        }
    },
    "applications": {
        "startup": {
            "type": "list",
            "items": {
                "type": "dict",
                "schema": {
                    "name": {"type": "string"},
                    "command": {"type": "string"},
                    "enabled": {"type": "boolean"}
                }
            }
        },
        "processes": {
            "stop": {"type": "list", "items": {"type": "string"}},
            "start": {
                "type": "list",
                "items": {
                    "type": "dict",
                    "schema": {
                        "name": {"type": "string"},
                        "path": {"type": "string"},
                        "arguments": {"type": "string"}
                    }
                }
            }
        }
    }
}
