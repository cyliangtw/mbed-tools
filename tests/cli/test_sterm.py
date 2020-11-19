#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from unittest import mock

import pytest

from click.testing import CliRunner

from mbed_tools.cli.sterm import sterm, MbedDevicesError


@mock.patch("mbed_tools.cli.sterm.terminal")
def test_launches_terminal_on_given_serial_port(mock_terminal):
    port = "tty.1111"
    CliRunner().invoke(sterm, ["--port", port])

    mock_terminal.run.assert_called_once_with(port, 9600, echo=True)


@mock.patch("mbed_tools.cli.sterm.terminal")
def test_launches_terminal_with_given_baud_rate(mock_terminal):
    port = "tty.1111"
    baud = 115200
    CliRunner().invoke(sterm, ["--port", port, "--baudrate", baud])

    mock_terminal.run.assert_called_once_with(port, baud, echo=True)


@mock.patch("mbed_tools.cli.sterm.terminal")
def test_launches_terminal_with_echo_off_when_specified(mock_terminal):
    port = "tty.1111"
    CliRunner().invoke(sterm, ["--port", port, "--echo", "off"])

    mock_terminal.run.assert_called_once_with(port, 9600, echo=False)


@mock.patch("mbed_tools.cli.sterm.terminal")
@mock.patch("mbed_tools.cli.sterm.get_connected_devices")
def test_attempts_to_detect_device_if_no_port_given(mock_get_devices, mock_terminal):
    CliRunner().invoke(sterm, [])

    mock_get_devices.assert_called_once()


@mock.patch("mbed_tools.cli.sterm.terminal")
@mock.patch("mbed_tools.cli.sterm.get_connected_devices")
def test_attempts_to_find_connected_target_if_target_given(mock_get_devices, mock_terminal):
    expected_port = "tty.k64f"
    mock_get_devices.return_value = mock.Mock(
        identified_devices=[mock.Mock(serial_port=expected_port, mbed_board=mock.Mock(board_type="K64F"))]
    )

    CliRunner().invoke(sterm, ["-m", "K64F"])

    mock_terminal.run.assert_called_once_with(expected_port, 9600, echo=True)


@mock.patch("mbed_tools.cli.sterm.terminal")
@mock.patch("mbed_tools.cli.sterm.get_connected_devices")
def test_returns_serial_port_for_first_device_detected_if_no_target_given(mock_get_devices, mock_terminal):
    expected_port = "tty.k64f"
    mock_get_devices.return_value = mock.Mock(
        identified_devices=[
            mock.Mock(serial_port=expected_port, mbed_board=mock.Mock(board_type="K64F")),
            mock.Mock(serial_port="tty.disco", mbed_board=mock.Mock(board_type="DISCO")),
        ]
    )

    CliRunner().invoke(sterm, [])

    mock_terminal.run.assert_called_once_with(expected_port, 9600, echo=True)


@mock.patch("mbed_tools.cli.sterm.terminal")
@mock.patch("mbed_tools.cli.sterm.get_connected_devices")
def test_raises_exception_if_given_target_not_found(mock_get_devices, mock_terminal):
    mock_get_devices.return_value = mock.Mock(
        identified_devices=[mock.Mock(serial_port="", mbed_board=mock.Mock(board_type="DISCO"))]
    )

    with pytest.raises(MbedDevicesError):
        CliRunner().invoke(sterm, ["-m", "K64F"], catch_exceptions=False)


@mock.patch("mbed_tools.cli.sterm.terminal")
@mock.patch("mbed_tools.cli.sterm.get_connected_devices")
def test_raises_exception_if_no_devices_detected(mock_get_devices, mock_terminal):
    mock_get_devices.return_value = mock.Mock(identified_devices=[])

    with pytest.raises(MbedDevicesError):
        CliRunner().invoke(sterm, ["-m", "K64F"], catch_exceptions=False)