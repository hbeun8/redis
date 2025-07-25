#!/usr/bin/env python3
import typer
from typing import Optional
from dataclasses import dataclass
from server import Server

app = typer.Typer()

@dataclass
class Args:
    l: str
    p: str
    i: Optional[str]
    x: Optional[str]
    z: Optional[str]
    c: Optional[str]
    e: Optional[str]
    a: Optional[str]

@app.command()
def main(
    l: str = typer.Option("tcp", "-l", help="Connection type", case_sensitive=False),
    p: str = typer.Option(8001, "-p", help="Port number or range (e.g., 8080 or 8880-8890)"),
    i: Optional[str] = typer.Option(None, "-i", help="Execute program and pipe I/O to/from socket"),
    x: Optional[str] = typer.Option(None, "-x", help="Executes hex dump sent by client"),
    z: Optional[str] = typer.Option(None, "-z", help="Checks if a server is listening on a specified port"),
    c: Optional[str] = typer.Option(None, "-c", help="Number of clients connected to the server"),
    e: Optional[str] = typer.Option(None, "-e", help="Echo Loop to the server"),
    a: Optional[str] = typer.Option(None, "-a", help="Ping Pong Toggle Loop"),
):
    print("Welcome!Redis Clone")

    if "-" in p:
        try:
            start_port, end_port = map(int, p.split("-"))
            ports = range(start_port, end_port + 1)
        except ValueError:
            typer.echo("Invalid port range format. Use: 8000-8005")
            raise typer.Exit(code=1)
    else:
        ports = [int(p)]

    args = Args(l=l, p=p, i=i, x=x, z=z, c=c, e=e, a=a)
    server = Server(args)

    try:
        server.start(ports)
        return server
    except KeyboardInterrupt:
        typer.echo("\nServer stopped by user")

if __name__ == "__main__":
    app()
