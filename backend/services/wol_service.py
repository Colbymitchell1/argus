import socket
import struct
import logging

logger = logging.getLogger("argus.wol")


def send_magic_packet(mac: str, broadcast: str = "192.168.50.255", port: int = 9) -> bool:
    """
    Send a WoL magic packet to the given MAC address.
    Magic packet = 6x 0xFF + 16x MAC address repeated.
    """
    try:
        # Normalize MAC — strip separators
        mac_clean = mac.replace(":", "").replace("-", "").replace(".", "")

        if len(mac_clean) != 12:
            raise ValueError(f"Invalid MAC address: {mac}")

        # Build magic packet
        mac_bytes = bytes.fromhex(mac_clean)
        magic_packet = b"\xff" * 6 + mac_bytes * 16

        # Send via UDP broadcast
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.connect((broadcast, port))
            sock.send(magic_packet)

        logger.info(f"Magic packet sent to {mac} via {broadcast}:{port}")
        return True

    except Exception as e:
        logger.error(f"WoL failed for {mac}: {e}")
        return False
