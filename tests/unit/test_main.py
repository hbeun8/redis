import typer
from typer.testing import CliRunner
from main import app
runner = CliRunner()

def test_port():
    result = runner.invoke(app, ["-p", "9000"])
    assert result.exit_code == 0
    assert "Port 9000 is open" in result.output


def test_port_range():
    result = runner.invoke(app, ["-p", "8900-8999"])
    assert result.exit_code == 0
    assert 'open' in result.output

def test_port_interactive():
    result = runner.invoke(app, ["-p", "9000", "-i", "I"])
    assert result.exit_code == 0
    assert 'Port 9000 is open' in result.output
