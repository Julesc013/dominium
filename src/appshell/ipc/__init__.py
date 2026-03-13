"""Shared AppShell IPC attach/detach surfaces."""

from .ipc_client import (
    attach_ipc_endpoint,
    detach_ipc_session,
    discover_ipc_endpoints,
    query_ipc_log_events,
    query_ipc_status,
    run_ipc_console_command,
)
from .ipc_endpoint_server import (
    AppShellIPCEndpointServer,
    clear_current_ipc_endpoint_server,
    get_current_ipc_endpoint_server,
    set_current_ipc_endpoint_server,
)
from .ipc_transport import (
    IPC_ENDPOINT_DESCRIPTOR_DIR_REL,
    IPC_ENDPOINT_MANIFEST_REL,
    build_console_io_message,
    build_ipc_endpoint_descriptor,
    build_ipc_frame,
    build_ipc_local_address,
    discover_ipc_endpoint_descriptor,
    discover_ipc_manifest,
    ipc_endpoint_descriptor_path,
)

__all__ = [
    "AppShellIPCEndpointServer",
    "IPC_ENDPOINT_DESCRIPTOR_DIR_REL",
    "IPC_ENDPOINT_MANIFEST_REL",
    "attach_ipc_endpoint",
    "build_console_io_message",
    "build_ipc_endpoint_descriptor",
    "build_ipc_frame",
    "build_ipc_local_address",
    "clear_current_ipc_endpoint_server",
    "detach_ipc_session",
    "discover_ipc_endpoint_descriptor",
    "discover_ipc_endpoints",
    "discover_ipc_manifest",
    "get_current_ipc_endpoint_server",
    "ipc_endpoint_descriptor_path",
    "query_ipc_log_events",
    "query_ipc_status",
    "run_ipc_console_command",
    "set_current_ipc_endpoint_server",
]
