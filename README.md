# Encrypted Client-Server on Raspberry Pi Zero 2 W

Two Raspberry Pi Zero 2 W boards communicating over TCP with symmetric encryption (Fernet/AES) and password authentication. Once logged in, the client remotely switches three LEDs wired to the server's GPIO pins.


| | |
|---|---|
| Hardware | 2x Raspberry Pi Zero 2 W, 3 LEDs (green, blue, red) on GPIO 18, 23, 24 |
| Language | Python 3 |
| Libraries | `socket`, `hashlib`, `cryptography` (Fernet), `RPi.GPIO` |
| Year | 2024 |

## Architecture

```
┌────────────────┐   Fernet-encrypted messages over TCP   ┌────────────────┐
│  Pi Zero 2 W   │ ─────────────────────────────────────► │  Pi Zero 2 W   │
│    CLIENT      │ ◄───────────────────────────────────── │    SERVER      │
│                │                                        │                │
│ - reads secret │                                        │ - generates    │
│   key file     │                                        │   Fernet key   │
│ - SHA-256 the  │                                        │ - stores hashed│
│   password     │                                        │   credentials  │
│ - sends cmds   │                                        │ - drives LEDs  │
└────────────────┘                                        └────────────────┘
```

## How it works

1. On start, the server generates a Fernet key and writes it to `secret.key`. The key is copied to the client manually.
2. The client asks for a username and password, computes the SHA-256 hash of the password, and sends `username:hash` encrypted with Fernet.
3. The server decrypts the message and compares the hash with its stored value. It replies `Authenticated` or `Authentication Failed`, also encrypted.
4. After login, the client sends commands (`led 1 on`, `led 1 off`, ... `exit`). The server decrypts each one and acts only on exact matches from a fixed list (a whitelist), so unknown commands do nothing.

## Security properties

- **Confidentiality and integrity in transit:** Fernet provides AES-128-CBC encryption with an HMAC-SHA256 authentication tag, so a network observer can't read messages and tampered messages fail to decrypt.
- **No plaintext passwords at rest:** the server stores SHA-256 hashes, not passwords.
- **Command whitelist:** only six exact LED commands and `exit` are ever acted on.

## Threat model

**Assets:** login credentials and the commands sent between client and server.
**Assumed attacker:** someone on the same network who can capture and modify traffic, and who may obtain a copy of the credential store.

| Defended against | How |
|---|---|
| Passive sniffing on the LAN | Fernet encryption |
| Modification of messages in transit | HMAC authentication tag |
| Plaintext password storage | SHA-256 hashing |
| Arbitrary command execution | Exact-match command whitelist |

### Known limitations (not defended against)

- **Pass-the-hash:** the client sends the hash, so the hash effectively *is* the password. Someone who steals the server's hash store can log in without cracking anything.
- **Unsalted, fast hash:** identical passwords produce identical hashes, and plain SHA-256 is cheap to brute-force. bcrypt, Argon2, or salted PBKDF2 would be the right choice.
- **Replay:** there's no nonce, session token, or timestamp check, so a captured encrypted login message could be replayed while the same key is in use.
- **Key management:** the pre-shared key is stored in plaintext, regenerated on each server start, and distributed by hand.
- **Fragile parsing:** a malformed or wrongly-encrypted message raises an exception and crashes the server (an easy denial of service). The server also handles one client at a time and assumes one message per `recv()`.
- **No rate limiting** on login attempts.
- **Lab-grade credentials:** a single hardcoded demo user, which is fine for a demo and not for anything real.

### What I'd improve next

- Replace SHA-256 with a salted, slow hash (bcrypt or Argon2), and hash on the server so the client sends the password only inside the encrypted channel
- Add a challenge-response or session token to stop replay
- Move from a pre-shared key to TLS with certificates, so keys aren't copied by hand
- Catch exceptions and close bad connections instead of crashing; add login attempt limits
- Support multiple clients and log authentication events


## Running it

```bash
pip install cryptography RPi.GPIO
```

1. On the server Pi, run `server.py`. It creates `secret.key`.
2. Copy `secret.key` to the client Pi.
3. Set the server's IP address in `client.py`, then run it and log in.


