# Copyright 2026 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");

"""Módulo de configuración para servidores MCP del proyecto Agency.

Este archivo configura y expone la conexión automatizada de bajo consumo
de memoria RAM al servidor de herramientas local secure-mcp.
"""

from google.antigravity.types import McpStdioServer

# Definición del servidor de herramientas local optimizado en Python envuelto en un Sandbox de Bubblewrap (bwrap)
# Esto confina su ejecución impidiendo el acceso a /home/fratfn y /Desarrollo excepto a su propio python y script.
secure_mcp_server = McpStdioServer(
    name="secure-mcp",
    command="/usr/bin/bwrap",
    args=[
        "--ro-bind", "/usr", "/usr",
        "--ro-bind", "/lib", "/lib",
        "--ro-bind", "/lib64", "/lib64",
        "--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf",
        "--ro-bind", "/etc/ssl", "/etc/ssl",
        "--ro-bind", "/etc/ca-certificates", "/etc/ca-certificates",
        "--dir", "/tmp",
        "--proc", "/proc",
        "--dev", "/dev",
        "--unshare-pid",
        "--unshare-ipc",
        "--unshare-uts",
        "--ro-bind", "/home/fratfn/vertex_env", "/home/fratfn/vertex_env",
        "--ro-bind", "/home/fratfn/.gemini/antigravity/scratch/secure-mcp", "/home/fratfn/.gemini/antigravity/scratch/secure-mcp",
        "/home/fratfn/vertex_env/bin/python",
        "/home/fratfn/.gemini/antigravity/scratch/secure-mcp/mcp_server.py"
    ]
)

# Lista global de servidores MCP que se inyectarán en la configuración del Agente
mcp_servers_list = [secure_mcp_server]
