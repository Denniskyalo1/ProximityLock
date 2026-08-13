Here's just the file — copy this entire block into `README.md`, replacing everything currently in it.

```markdown
# ProximityLock

Automatically locks your Windows laptop when your phone goes out of Bluetooth range, and shuts the laptop down if it stays out of range too long. Your phone acts as a physical "key" — no app required on the phone, just an existing Bluetooth pairing.

## How it works

The script polls your phone's live Bluetooth connection status using the Windows WinRT API. If the connection is missing for several checks in a row, it locks the screen. If it stays missing even longer, it shuts the laptop down. Each check retries a few times with short delays first, so a brief Bluetooth blip (which happens naturally even when the phone is right next to the laptop) doesn't cause a false lock or shutdown.

## Requirements

- Windows 10/11 with a working Bluetooth adapter
- Python 3.10+
- Your phone paired with your laptop over Bluetooth (regular pairing via Windows Settings, no app needed)

## Setup

### 1. Clone the repo and install dependencies

```powershell
git clone https://github.com/Denniskyalo1/ProximityLock.git
cd ProximityLock
pip install -r requirements.txt
```

### 2. Pair your phone with your laptop

Go to **Settings → Bluetooth & devices → Add device** on your laptop, and pair it with your phone like you normally would (confirm the code on both sides).

### 3. Find your phone's Bluetooth address

Open PowerShell and run:

```powershell
Get-PnPDevice -Class Bluetooth | Select-Object FriendlyName, Status, InstanceId | Format-Table -AutoSize
```

Look through the list for the row where `FriendlyName` matches your phone's name. The `InstanceId` column will contain something like:

```
BTHENUM\DEV_28024443D815\...
```

Take the 12 characters after `DEV_` (in this example, `28024443D815`) and prefix them with `0x` — that gives you `0x28024443D815`. This is your `PHONE_ADDRESS`.

### 4. Create your `.env` file

Copy the example file:

```powershell
copy .env.example .env
```

Open `.env` and set your phone's address:

```
PHONE_ADDRESS=0xYOURADDRESSHERE
```

### 5. Test it manually

```powershell
python proximity_lock.py
```

Leave your phone connected for a bit, then turn its Bluetooth off (or walk away with it) and confirm the laptop locks after a few missed checks, then shuts down if it stays disconnected. Stop the script anytime with `Ctrl+C`.

Check `proximity_lock.log` (created automatically in the project folder) to see a timestamped record of every check, lock, and shutdown event — useful for tuning the settings below.

### 6. (Optional) Run it automatically at login

Use Windows Task Scheduler:

1. Open **Task Scheduler** → **Create Task**.
2. **General tab**: check "Run whether user is logged on or not."
3. **Triggers tab**: New → "At log on."
4. **Actions tab**: New → "Start a program":
   - Program/script: full path to `python.exe`
   - Add arguments: full path to `proximity_lock.py`
   - Start in: the ProximityLock folder path
5. **Conditions tab**: uncheck "Start only on AC power" if you want it active on battery too.
6. Save and enter your Windows password when prompted.

## Configuration (`.env`)

| Variable | Meaning | Default |
|---|---|---|
| `PHONE_ADDRESS` | Your phone's Bluetooth address (see setup step 3) | required |
| `CHECK_INTERVAL` | Seconds between each connection check | 10 |
| `LOCK_AFTER` | Consecutive missed checks before locking | 3 |
| `SHUTDOWN_AFTER` | Consecutive missed checks before shutting down | 15 |
| `RETRY_ATTEMPTS` | Retries within a single check before counting it as missed | 3 |
| `RETRY_DELAY` | Seconds between retries within a check | 2 |

With the defaults, a lock happens roughly 30 seconds after the phone leaves range, and shutdown roughly 2.5 minutes after that — adjust these numbers to fit how strict or lenient you want it.

## Troubleshooting

- **False locks while the phone is right next to the laptop**: Bluetooth idle-disconnects can happen even with the phone in range. Try increasing `RETRY_ATTEMPTS`, `RETRY_DELAY`, or `LOCK_AFTER`.
- **Script can't find the phone at all**: double-check `PHONE_ADDRESS` matches exactly what you found in step 3, including the `0x` prefix.
- **`pip` not recognized**: Python wasn't added to PATH during install — reinstall Python and check "Add python.exe to PATH."

## Disclaimer

This shuts your laptop down automatically based on Bluetooth signal — test thoroughly with your own devices before relying on it daily, and make sure you're comfortable with the lock/shutdown timing before leaving it running unattended.
```